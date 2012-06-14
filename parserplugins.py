import os
import re

class ParserPlugins:

	_parsers = {
		'mimetypes': {},
		'expressions': {},
		'extensions': {}
	}

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

			types = obj.types()

			# map types to this parser
			for key in types.keys():
				for type_ in types[key]:
					self._parsers[key][type_] = obj			


	def get(self, mimetype, extension):
		'''Returns a suitable parser plugin for the given mimetype and extension'''

		# match by extension
		if extension and extension in self._parsers['extensions']:
			return self._parsers['extensions'][extension]

		if mimetype:
			# look for direct mimetype match
			if mimetype in self._parsers:
				return self._parsers['mimetypes'][mimetype]

			# try to see if mimetypes matches any of the regexps
			for expression in self._parsers['expressions']:
				if re.match(expression, mimetype):
					return self._parsers['expressions'][expression]

		# return fallback parser
		return self._parsers['mimetypes'][None]

