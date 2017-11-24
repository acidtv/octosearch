import ldap


class LDAPHelper:

    _conn = None

    def connect(self):
        self._conn = ldap.initialize('ldap://yourldapserver')
        self._conn.set_option(ldap.OPT_REFERRALS, 1)

    def authenticate(self, username, password):
        self._conn.bind_s(username, password)

    def user_info(self):
        info_result_id = self._conn.search('ou=ARI,dc=ari,dc=local', ldap.SCOPE_SUBTREE, 'cn=username', ['cn', 'objectSid', 'memberof'])
        info_results = self._conn.result(info_result_id)
        return info_results

    def user_groups(self):
        groups_result_id = self._conn.search('ou=ARI,dc=ari,dc=local', ldap.SCOPE_SUBTREE, '(|(cn=IT)(cn=Webteam)(cn=sshusers))', ['cn', 'objectSid'])
        groups_results = self._conn.result(groups_result_id)
        return groups_results
