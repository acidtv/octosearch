import re
import plugins

class ParserPlugins(plugins.Plugins):

	_parsers = {
		'mimetypes': {},
		'expressions': {},
		'extensions': {}
	}

	_type = 'parser'

	def __init__(self):
		"""Load parsers to see which mimetypes they want
		to take care of"""

		for plugin in self.list_plugins():
			obj = self.load(plugin)
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
			if mimetype in self._parsers['mimetypes']:
				return self._parsers['mimetypes'][mimetype]

			# try to see if mimetypes matches any of the regexps
			for expression in self._parsers['expressions']:
				if re.match(expression, mimetype):
					return self._parsers['expressions'][expression]

		# return fallback parser
		return self._parsers['mimetypes'][None]

