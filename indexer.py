import sys
import os
import os.path
import mimetypes
import hashlib

class Indexer:
	logger = None
	output = None

	parsers = {}

	def __init__(self, logger, output):
		self.logger = logger
		self.output = output
		self.init_parsers()

	def directory(self, root):
		"""Index a directory"""

		stack = [root]

		# walk filesystem
		while stack:
			path = stack.pop()

			for file in os.listdir(path):
				full_path = path + '/' + file

				if os.path.isdir(full_path):
					stack.append(full_path)
					continue

				self.file(path, file)

	def file(self, path, file):
		'''Index a file'''

		file_full = path + '/' + file
		mimetype = mimetypes.guess_type(file_full)[0]
		parser = self.get_parser(mimetype)

		self.logger.add(file_full + '(' + str(mimetype) + ')')

		statdata = os.stat(file_full)

		info = {}
		info['filename'] = file
		info['path'] = path
		info['mimetype'] = mimetype
		info['created'] = statdata.st_ctime
		info['modified'] = statdata.st_mtime
		info['content'] = parser.parse(file_full)

		id = hashlib.md5(file_full).hexdigest()

		self.output.add(id, info)

	def check_removed(self):
		'''Check the index for removed files'''

		self.logger.add('Checking index for removed files...')

		documents = self.output.get_all()

		for document in documents:
			self.logger.add(document)
			i = 0

	def get_parser(self, mimetype):
		if mimetype in self.parsers:
			return self.parsers[mimetype]
		else:
			# return fallback parser
			return self.parsers[None]

	def init_parsers(self):
		"""Load parsers to see which mimetypes they want 
		to take care of"""

		for file in os.listdir('./parsers/'):
			if file[-3:] != '.py' or file[:1] == '_':
				continue

			class_name = 'Parser_' + file[:-3].capitalize()
			module_name = 'parsers.' + file[:-3].lower()

			self.logger.add('Loading ' + module_name)

			mod = __import__(module_name, globals(), locals(), [class_name])
			obj = getattr(mod, class_name)()

			mimes = obj.mime_types()

			for mimetype in mimes:
				self.parsers[mimetype] = obj
