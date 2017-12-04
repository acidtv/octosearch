from subprocess import check_output
import os.path
from . import localfs


class Mountedcifs(localfs.Localfs):

    # Docs on SID's: https://msdn.microsoft.com/en-us/library/windows/desktop/aa379649(v=vs.85).aspx

    ACE_ACCESS_ALLOWED = 0
    ACE_ACCESS_DENIED = 1

    # Types from https://github.com/Distrotech/cifs-utils/blob/distrotech-cifs-utils/cifsacl.h

    # D | RC | P | O | S | R | W | A | E | DC | REA | WEA | RA | WA
    ACE_TYPE_FULL_CONTROL = 0x001f01ff

    # RC | S | R | E | REA | RA
    ACE_TYPE_EREAD = 0x001200a9

    # RC | S | R | E | REA | GR | GE
    ACE_TYPE_OREAD = 0xa01200a1

    # RC | S | R | REA | RA
    ACE_TYPE_BREAD = 0x00120089

    # W | A | WA | WEA
    ACE_TYPE_EWRITE = 0x00000116

    # D | RC | S | R | W | A | E |REA | WEA | RA | WA
    ACE_TYPE_CHANGE = 0x001301bf

    # GR | RC | REA | RA | REA | R
    ACE_TYPE_ALL_READ_BITS = 0x80020089

    # WA | WEA | A | W
    ACE_TYPE_ALL_WRITE_BITS = 0x40000116

    def process_file(self, path, file):
        id, info = super(Mountedcifs, self).process_file(path, file)
        info.update(self.cifs_info(path, file))

        return id, info

    def cifs_info(self, path, file):
        output = check_output(['getcifsacl', '-r', os.path.join(path, file)])

        acl = self.parse_cifsacl(output)
        allowed = self.filter_acl_read(acl, self.ACE_ACCESS_ALLOWED)
        denied = self.filter_acl_read(acl, self.ACE_ACCESS_DENIED)

        info = {'read_perms': }

        return info

    def parse_cifsacl(self, data):
        '''Parse Access Control List'''
        read_perms = []

        for line in data.split("\n"):
            user = self.parse_cifsace(line)
            if (user):
                read_perms.append(user)

        return read_perms

    def parse_cifsace(self, line):
        '''Parse Access Control Entry'''
        parts = line.split(':')
        ace = {}

        if (parts[0] == 'ACL'):
            ace['sid'] = parts[1]

            permission_parts = parts[2].split('/')

            # convert hex strings to int
            ace['access'] = int(permission_parts[0], 0)
            ace['mask'] = int(permission_parts[2], 0)

            # check if access allowed
            if ace['access'] != self.ACE_ACCESS_ALLOWED:
                return

            # check for read access
            if (((ace['mask'] & self.ACE_TYPE_FULL_CONTROL) != self.ACE_TYPE_FULL_CONTROL)
                    and ((ace['mask'] & self.ACE_TYPE_EREAD) != self.ACE_TYPE_EREAD)
                    and ((ace['mask'] & self.ACE_TYPE_BREAD) != self.ACE_TYPE_BREAD)
                    and ((ace['mask'] & self.ACE_TYPE_OREAD) != self.ACE_TYPE_OREAD)):
                return

            return ace

    def filter_acl_read(self, acl, ace_access):
        for ace in acl:
            # check if access allowed
            if ace['access'] != ace_access:
                continue

            # check for read access
            if (((ace['mask'] & self.ACE_TYPE_FULL_CONTROL) != self.ACE_TYPE_FULL_CONTROL)
                    and ((ace['mask'] & self.ACE_TYPE_EREAD) != self.ACE_TYPE_EREAD)
                    and ((ace['mask'] & self.ACE_TYPE_BREAD) != self.ACE_TYPE_BREAD)
                    and ((ace['mask'] & self.ACE_TYPE_OREAD) != self.ACE_TYPE_OREAD)):
                continue

            yield ace

    def acl_sids(self, acl):
        return

    def format_sid(raw_value):
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

