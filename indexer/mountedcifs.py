from subprocess import check_output
import os.path
import localfs

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
	ACE_TYPE_ALL_WRITE_BITS	= 0x40000116

	def process_file(self, path, file):
		id, info = super(Mountedcifs, self).process_file(path, file)

		return id, info.update(self.cifs_info(path, file))

	def cifs_info(self, path, file):
		output = check_output(['getcifsacl', '-r', os.path.join(path, file)])

		info = {'read_perms': self.parse_cifsacl(output)}

		return info

	def parse_cifsacl(self, data):
		read_perms = []

		for line in data.split("\n"):
			user = self.user_allowed(line)
			if (user):
				read_perms.append(user)

		return read_perms

	def user_allowed(self, line):
		parts = line.split(':')

		if (parts[0] == 'ACL'):
			user = parts[1]

			permission_parts = parts[2].split('/')

			# convert hex strings to int
			access = int(permission_parts[0], 0)
			mask = int(permission_parts[2], 0)

			# check if access allowed
			if access != self.ACE_ACCESS_ALLOWED:
				return

			# check for read access
			if (((mask & self.ACE_TYPE_FULL_CONTROL) != self.ACE_TYPE_FULL_CONTROL)
				and ((mask & self.ACE_TYPE_EREAD) != self.ACE_TYPE_EREAD)
				and ((mask & self.ACE_TYPE_BREAD) != self.ACE_TYPE_BREAD)
				and ((mask & self.ACE_TYPE_OREAD) != self.ACE_TYPE_OREAD)):
				return

			return user
