from . import app, conf
from flask import render_template, request, session
from .. import backends, plugins
from werkzeug.exceptions import abort
import ConfigParser


@app.context_processor
def template_vars():
    username = session['username'] if 'username' in session else ''
    has_auth_backend = True

    try:
        conf.get('auth')
    except ConfigParser.NoSectionError:
        has_auth_backend = False

    return dict(
        username=username,
        has_auth_backend=has_auth_backend
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    success = None
    if request.method == 'POST':
        success = auth()

    return render_template('login.html', success=success)


@app.route('/search')
def search():
    backend = get_backend()

    page = 1

    if 'page' in request.args and request.args['page']:
        try:
            page = int(request.args['page'])
        except ValueError:
            abort(404)

    results = backend.search(query_str=request.args['q'], page=page)

    if len(results['hits']) == 0:
        abort(404)

    return render_template(
        'search.html',
        results=results,
        query=request.args['q'],
        page=page,
        found=results['found'],
        next_page=None if len(results['hits']) < backend.pagesize() else page + 1,
        prev_page=None if page <= 1 else page - 1
    )


def get_backend():
    backend = backends.elasticsearch.BackendElasticSearch(conf.get('backend', 'server'), conf.get('backend', 'index'))

    if 'auth' in session:
        backend.auth(session['auth'], session['groups'])

    return backend


def auth():
    auth_driver = plugins.get('auth', conf.get('auth', 'driver'))(conf.get('auth'))

    if not auth_driver.authenticate(request.form['username'], request.form['password']):
        return False

    session['auth'] = conf.get('auth', 'name')
    session['groups'] = auth_driver.groups()
    session['username'] = request.form['username']

    return True
