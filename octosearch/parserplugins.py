import plugins


class ParserPlugins(object):

    _parsers = {
            'mimetypes': {},
            # 'extensions': {}
            }

    _fallback_mimetype = 'application/octet-stream'

    def __init__(self):
        """Load parsers to see which mimetypes they want
            to take care of"""

        for plugin in plugins.list('parser'):
            self._parsers['mimetypes'][plugin.name] = plugin

    def have(self, mimetype):
        '''Returns TRUE if parser for mimetype exists, FALSE otherwise'''

        return mimetype in self._parsers['mimetypes']

    def get(self, mimetype):
        '''Returns a suitable parser plugin for the given mimetype and extension'''

        # match by extension
        # if extension and extension in self._parsers['extensions']:
        #     return self._parser_factory('extensions', extension)

        if mimetype:
            # look for direct mimetype match
            if mimetype in self._parsers['mimetypes']:
                return self._parser_factory('mimetypes', mimetype)

        # return fallback parser
        # return self._parser_factory('mimetypes', self._fallback_mimetype)

    def _parser_factory(self, parsertype, key):
        return self._parsers[parsertype][key].load()()
