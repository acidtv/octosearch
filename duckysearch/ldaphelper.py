import ldap
from binascii import hexlify


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
        '''Make set of group_dns sid's, and of the groups the group_dns are a member of'''
        groups = []

        for group_dn in group_dns:
            group = self.entry(group_dn, ['objectSid', 'memberOf'])

            # debug group CN
            print group[1][0][0]

            # FIXME if `group` is not a security group continue?

            sid = self.format_sid(group[1][0][1]['objectSid'][0])
            groups.append(sid)

            if 'memberOf' in group[1][0][1]:
                groups.extend(self.groups(group[1][0][1]['memberOf']))

        return set(groups)

    def entry(self, dn, attrlist=None):
        dn_result = self._conn.search(dn, ldap.SCOPE_BASE, '(objectclass=*)', attrlist=attrlist)
        return self._conn.result(dn_result)

    def format_sid(self, raw_value):
        """
        From: https://github.com/cannatag/ldap3/blob/master/ldap3/protocol/formatters/formatters.py
        """
        '''
        SID= "S-1-" IdentifierAuthority 1*SubAuthority
               IdentifierAuthority= IdentifierAuthorityDec / IdentifierAuthorityHex
                  ; If the identifier authority is < 2^32, the
                  ; identifier authority is represented as a decimal
                  ; number
                  ; If the identifier authority is >= 2^32,
                  ; the identifier authority is represented in
                  ; hexadecimal
                IdentifierAuthorityDec =  1*10DIGIT
                  ; IdentifierAuthorityDec, top level authority of a
                  ; security identifier is represented as a decimal number
                IdentifierAuthorityHex = "0x" 12HEXDIG
                  ; IdentifierAuthorityHex, the top-level authority of a
                  ; security identifier is represented as a hexadecimal number
                SubAuthority= "-" 1*10DIGIT
                  ; Sub-Authority is always represented as a decimal number
                  ; No leading "0" characters are allowed when IdentifierAuthority
                  ; or SubAuthority is represented as a decimal number
                  ; All hexadecimal digits must be output in string format,
                  ; pre-pended by "0x"
        Revision (1 byte): An 8-bit unsigned integer that specifies the revision level of the SID. This value MUST be set to 0x01.
        SubAuthorityCount (1 byte): An 8-bit unsigned integer that specifies the number of elements in the SubAuthority array. The maximum number of elements allowed is 15.
        IdentifierAuthority (6 bytes): A SID_IDENTIFIER_AUTHORITY structure that indicates the authority under which the SID was created. It describes the entity that created the SID. The Identifier Authority value {0,0,0,0,0,5} denotes SIDs created by the NT SID authority.
        SubAuthority (variable): A variable length array of unsigned 32-bit integers that uniquely identifies a principal relative to the IdentifierAuthority. Its length is determined by SubAuthorityCount.
        '''

        if str is not bytes:  # Python 3
            revision = int(raw_value[0])
            sub_authority_count = int(raw_value[1])
            identifier_authority = int.from_bytes(raw_value[2:8], byteorder='big')
            if identifier_authority >= 4294967296:  # 2 ^ 32
                identifier_authority = hex(identifier_authority)

            sub_authority = ''
            i = 0
            while i < sub_authority_count:
                sub_authority += '-' + str(int.from_bytes(raw_value[8 + (i * 4): 12 + (i * 4)], byteorder='little'))  # little endian
                i += 1
        else:  # Python 2
            revision = int(ord(raw_value[0]))
            sub_authority_count = int(ord(raw_value[1]))
            identifier_authority = int(hexlify(raw_value[2:8]), 16)
            if identifier_authority >= 4294967296:  # 2 ^ 32
                identifier_authority = hex(identifier_authority)

            sub_authority = ''
            i = 0
            while i < sub_authority_count:
                sub_authority += '-' + str(int(hexlify(raw_value[11 + (i * 4): 7 + (i * 4): -1]), 16))  # little endian
                i += 1
        return 'S-' + str(revision) + '-' + str(identifier_authority) + sub_authority
