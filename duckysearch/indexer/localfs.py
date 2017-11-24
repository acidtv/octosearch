import sys
import os
import os.path
import mimetypes
import hashlib

class Localfs:
	_logger = None
	_output = None
	_plugins = None

	_ignore_mimetypes = []
	_ignore_extensions = []

	def __init__(self, logger, output, plugins):
		self._logger = logger
		self._output = output
		self._plugins = plugins
		#self.init_parsers()

	def directory(self, root):
		"""Index a directory"""

		dirstack = [root]

		# walk filesystem
		while dirstack:
			path = dirstack.pop()
			filestack = {}

			#self.logger.add(path)

			for file in os.listdir(path):
				full_path = os.path.join(path, file)

				# if dir add to stack
				if os.path.isdir(full_path):
					dirstack.append(full_path)
					continue

				# save files to check modified date later
				statdata = os.stat(full_path)
				filestack[hashlib.md5(full_path).hexdigest()] = {'file': file, 'path': path, 'stat': statdata}

			if not filestack:
				continue

			documents = self._output.get_keys(filestack.keys())

			for document in documents:
				# compare modified date from index with filesystem
				file = filestack.pop(document['id'])
				if file['stat'].st_mtime > document['modified']:
					self.file(file['path'], file['file'])

			# new files
			for file in filestack:
				self.file(filestack[file]['path'], filestack[file]['file'])

	def index_file(self, path, file):
		id, info = self.process_file(self, path, file)
		self._output.add(id, info)

	def process_file(self, path, file):
		'''Index a file'''

		file_full = os.path.join(path, file)

		mimetype = self._get_mimetype(file_full)
		extension = self._get_extension(file)
		statdata = os.stat(file_full)

		self._logger.add(file_full + ' (' + str(mimetype) + ')')

		call_parser = True

		if extension in self._ignore_extensions:
			call_parser = False

		if mimetype in self._ignore_mimetypes:
			call_parser = False

		content = ''

		if call_parser:
			parser = self._plugins.get(mimetype, extension)

			content = parser.parse(file_full, statdata)

			if not isinstance(content, str):
				raise Exception

			extra = parser.extra()

			if not isinstance(extra, dict):
				raise Exception

		info = {}
		info['filename'] = file
		info['path'] = path
		info['mimetype'] = mimetype
		info['created'] = statdata.st_ctime
		info['modified'] = statdata.st_mtime
		info['content'] = content
		info['extra'] = extra

		id = hashlib.md5(file_full).hexdigest()

		return (id, info)

	def check_removed(self):
		'''Check the index for removed files'''

		self._logger.add('Checking index for removed files...')

		removed = []
		documents = self._output.get_all()

		for document in documents:
			file_full = os.path.join(document['path'], document['filename'])
			if not os.path.isfile(file_full):
					self._logger.add('Removed: ' + file_full)
					removed.append(document['id'])

		if removed:
			self._logger.add('Waiting for search engine to process removed files...')
			self._output.remove(removed)

	def ignore_mimetypes(self, mimetypes):
		self._ignore_mimetypes = mimetypes

	def ignore_extensions(self, extensions):
		self._extensions = extensions

	def _get_extension(self, file):
		info = file.rpartition(os.extsep)

		if info[0] != '' and info[2] != '':
			return info[2]

		return ''

	def _get_mimetype(self, file):
		mimetype = mimetypes.guess_type(file)[0]
		return mimetype

