from . import app, conf, protocol
from flask import render_template, request, session, redirect, url_for, flash
from .. import backends, plugins
from werkzeug.exceptions import abort
import os.path


def login_redir():
    if 'username' in session:
        return

    if conf.get('web', 'login-required') == 'False':
        for indexer in conf.get('indexer'):
            if 'auth' not in indexer:
                # non-auth'ed source found, so login not needed
                return

    return redirect(url_for('login'))


@app.context_processor
def template_vars():
    has_auth_backend = True

    if conf.get('auth') is None:
        has_auth_backend = False

    vars = dict(
        username=username(),
        has_auth_backend=has_auth_backend,
    )

    user = username()

    if user:
        vars['register_url'] = protocol.register(
            request.host_url,
            conf.get('web', 'protocol-secret'),
            username()
        )

    return vars


@app.route('/')
def index():
    redir = login_redir()
    if redir:
        return redir
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if auth():
            return redirect(url_for('index'))
        else:
            flash('Login failed', 'error')

    return render_template(
        'login.html',
        auth_config=get_auth_config()
    )


@app.route('/search')
def search():
    redir = login_redir()
    if redir:
        return redir

    backend = get_backend()

    page = 1

    if 'page' in request.args and request.args['page']:
        try:
            page = int(request.args['page'])
        except ValueError:
            abort(404)

    results = backend.search(query_str=request.args['q'], page=page)
    enum_hits = list(results['hits'])
    nr_hits = len(enum_hits)

    if nr_hits == 0 and page > 1:
        abort(404)

    next_page = None if nr_hits < backend.pagesize() else page + 1
    prev_page = None if page <= 1 else page - 1
    prepared_hits = prepare_hits(enum_hits)

    return render_template(
        'search.html',
        results=results,
        hits=prepared_hits,
        query=request.args['q'],
        found=results['found'],
        page=page,
        next_page=next_page,
        prev_page=prev_page
    )


def prepare_hits(hits):
    '''Add the file extension for displaying icon. Guess based on mimetype'''

    for hit in hits:
        if hit['mimetype']:
            try:
                hit['extension'] = os.path.splitext(hit['url'])[1].strip('.')[:3]
            except TypeError:
                hit['extension'] = ''

        # Add link to client protocol handler
        if username():
            hit['octosearch_url'] = protocol.open(
                hit['url'],
                conf.get('web', 'protocol-secret'),
                username()
            )

        yield hit

def use_client_protocol(url):
    browser_protocols = ['http', 'https', 'ftp']

    match = re.match('([a-z]+)\:')

def get_backend():
    backend = backends.elasticsearch.BackendElasticSearch(conf.get('backend', 'server'), conf.get('backend', 'index'))

    if 'auth' in session:
        backend.auth(session['auth'], session['groups'])

    return backend


def auth():
    auth_config = get_auth_config()
    auth_driver = plugins.get('auth', auth_config['driver'])(auth_config)

    if not auth_driver.authenticate(request.form['username'], request.form['password']):
        return False

    session['auth'] = conf.get('auth', 'name')
    session['groups'] = auth_driver.groups()
    session['username'] = request.form['username']

    flash('You were successfully logged in to %s' % conf.get('auth', 'name'), 'success')

    return True


def get_auth_config():
    return conf.get('auth')


def username():
    return session['username'] if 'username' in session else ''
