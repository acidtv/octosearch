import plugins


class ParserPlugins(object):

    _parsers = {
            'mimetypes': {},
            'extensions': {}
            }

    def __init__(self):
        """Load parsers to see which mimetypes they want
            to take care of"""

        for plugin in plugins.list('parser'):
            self._parsers['mimetypes'][plugin.name] = plugin

    def get(self, mimetype, extension):
        '''Returns a suitable parser plugin for the given mimetype and extension'''

        # match by extension
        if extension and extension in self._parsers['extensions']:
            return self._parsers['extensions'][extension].load()()

        if mimetype:
            # look for direct mimetype match
            if mimetype in self._parsers['mimetypes']:
                return self._parsers['mimetypes'][mimetype].load()()

        # return fallback parser
        return self._parsers['mimetypes'][None].load()
