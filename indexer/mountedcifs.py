from subprocess import check_output
import os.path

class Mountedcifs(localfs.Localfs):

	def process_file(self, path, file):
		id, info = super(Mountedcifs, self).process_file(path, file)

		return id, info.update(self.cifs_info(path, file))

	def cifs_info(path, file):
		output = check_output(['getcifsacl', os.path.join(path, file)])

		info = {'read_perms': self.parse_cifsacl(output)}

		return info

	def parse_cifsacl(data):
		read_perms = []

		for line in data.split("\n"):
			user = self.parse_line(line)

			if (user):
				read_perms.append(user)

		return read_perms

	def parse_line(line):
		parts = line.split(':')

		if (parts[0] == 'ACL'):
			user = parts[1]

			permisson_parts = parts[2].split('/')

			if permission_parts[0] == 'ALLOWED':
				return user



