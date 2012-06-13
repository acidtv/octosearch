import os

class ParserPlugins:

	_parsers = {}

	def __init__(self):
		"""Load parsers to see which mimetypes they want 
		to take care of"""

		for file in os.listdir('./parsers/'):
			if file[-3:] != '.py' or file[:1] == '_':
				continue

			class_name = 'Parser' + file[:-3].capitalize()
			module_name = 'parsers.' + file[:-3].lower()

			mod = __import__(module_name, globals(), locals(), [class_name])
			obj = getattr(mod, class_name)()

			mimes = obj.mime_types()

			for mimetype in mimes:
				self._parsers[mimetype] = obj

	def get(self, mimetype, extension):
		'''Returns a suitable parser plugin for the given mimetype and extension'''

		if mimetype in self._parsers:
			return self._parsers[mimetype]
		else:
			# return fallback parser
			return self._parsers[None]

