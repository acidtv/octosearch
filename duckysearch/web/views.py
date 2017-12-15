from . import app, conf
from flask import render_template, request, session
from .. import ldaphelper, outputs


@app.context_processor
def template_vars():
    username = session['username'] if 'username' in session else ''
    return dict(
        username=username
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        ldap = ldaphelper.LDAPHelper(conf.get('ldap', 'server'), conf.get('ldap', 'search'))
        ldap.connect()
        ldap.authenticate(request.form['username'], request.form['password'])
        info = ldap.user_info(request.form['username'])

        session['groups'] = list(ldap.groups(info[1]['memberOf']))
        session['username'] = request.form['username']

    return render_template('login.html')


@app.route('/search')
def search():
    results = output().search(request.args['search'])
    return render_template('search.html', results=results)


def output():
    output = outputs.elasticsearch.OutputElasticSearch(conf.get('backend', 'server'), conf.get('backend', 'index'))

    if 'groups' in session:
        output.permissions(session['groups'])

    return output
