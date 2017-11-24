import ldap


class LDAPHelper:

    _conn = None
    _server = None
    _search = None

    def __init__(self, server, search=''):
        self._server = server
        self._search = search

    def connect(self):
        self._conn = ldap.initialize('ldap://' + self._server)
        self._conn.set_option(ldap.OPT_REFERRALS, 1)

    def authenticate(self, username, password):
        self._conn.bind_s(username, password)

    def user_info(self, username):
        info_result_id = self._conn.search(self._search, ldap.SCOPE_SUBTREE, 'cn=' + username, ['cn', 'objectSid', 'memberof'])
        info_results = self._conn.result(info_result_id)
        return info_results[1][0]

    def groups(self, groups):
        groups = ['cn=IT']
        search = ')('.join(groups)
        search = '(|(' + search + ')(cn=IT))'
        print self._search, search
        # groups_result_id = self._conn.search(self._search, ldap.SCOPE_SUBTREE, '(|(cn=IT)(cn=Webteam)(cn=sshusers))', ['cn', 'objectSid'])
        groups_result_id = self._conn.search(self._search, ldap.SCOPE_SUBTREE, search, ['cn', 'objectSid'])
        groups_results = self._conn.result(groups_result_id)
        return groups_results
