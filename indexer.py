import sys
import os
import os.path
import mimetypes
import hashlib

class Indexer:
	_logger = None
	_output = None
	_plugins = None

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


	def file(self, path, file):
		'''Index a file'''

		file_full = os.path.join(path, file)
		mimetype = mimetypes.guess_type(file_full)[0]
		extension = self._get_extension(file)

		parser = self._plugins.get(mimetype, extension)

		self._logger.add(file_full + ' (' + str(mimetype) + ')')

		statdata = os.stat(file_full)

		info = {}
		info['filename'] = file
		info['path'] = path
		info['mimetype'] = mimetype
		info['created'] = statdata.st_ctime
		info['modified'] = statdata.st_mtime
		info['content'] = parser.parse(file_full)

		id = hashlib.md5(file_full).hexdigest()

		self._output.add(id, info)

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

	def _get_extension(self, file):
		info = file.rpartition(os.extsep)

		if info[0] != '' and info[2] != '':
			return info[2]

		return ''

