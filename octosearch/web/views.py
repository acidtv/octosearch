from . import app, conf
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
    username = session['username'] if 'username' in session else ''
    has_auth_backend = True

    if conf.get('auth') is None:
        has_auth_backend = False

    return dict(
        username=username,
        has_auth_backend=has_auth_backend
    )


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

    if len(results['hits']) == 0 and page > 1:
        abort(404)

    next_page = None if len(results['hits']) < backend.pagesize() else page + 1
    prev_page = None if page <= 1 else page - 1
    results['hits'] = prepare_hits(results['hits'])

    return render_template(
        'search.html',
        results=results,
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

        yield hit


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
