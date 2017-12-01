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
        info_result_id = self._conn.search(self._search, ldap.SCOPE_SUBTREE, 'cn=' + username, ['cn', 'objectSid', 'memberof', 'primaryGroupId'])
        info_results = self._conn.result(info_result_id)
        return info_results[1][0]

    def groups(self, group_dns):
        # FIXME create graph of related groups
        groups = []

        for group_dn in group_dns:
            groups.append(self.entry(group_dn, ['objectSid', 'memberOf']))

        return groups

    def entry(self, dn, attrlist=None):
        dn_result = self._conn.search(dn, ldap.SCOPE_BASE, '(objectclass=*)', attrlist=attrlist)
        return self._conn.result(dn_result)
