Ducky
=====

Requirements
------------

 * pipenv
 * flask
 * python-ldap

mountedcifs:

 * getcifsacls

Development
-----------

To start the web interface: 

 $ export FLASK_APP=web/webserver.py && export FLASK_DEBUG=1 && pipenv run flask run


LDAP Notes
----------

 # connect to ldap
 import ldap
 conn = ldap.initialize('ldap://yourldapserver')
 conn.set_option(ldap.OPT_REFERRALS, 1)

 # auth
 conn.bind_s(username, password)

 # get user info
 info_result_id = conn.search('ou=ARI,dc=ari,dc=local', ldap.SCOPE_SUBTREE, 'cn=username', ['cn', 'objectSid', 'memberof'])
 info_results = conn.result(search_result_id)

 # find user groups
 groups_result_id = conn.search('ou=ARI,dc=ari,dc=local', ldap.SCOPE_SUBTREE, '(|(cn=IT)(cn=Webteam)(cn=sshusers))', ['cn', 'objectSid'])
 groups_results = conn.result(groups_result_id)

