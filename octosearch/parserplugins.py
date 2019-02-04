from . import plugins


class ParserPlugins(object):

    _parsers = {}

    _mimetypes = {}

    _parserconf = {}

    def __init__(self, conf, parserconf):
        """Load parsers to see which mimetypes they want
            to take care of"""

        self._parserconf = parserconf

        # load parsers registered with setuptools
        for plugin in plugins.list('parser'):
            self._parsers[plugin.name] = plugin.load()

        # map mimetypes to parsers
        for plugin in self._parsers:
            mimetypes = self._parser_factory(plugin).types()

            for mimetype in mimetypes:
                self._mimetypes[mimetype] = plugin

        # add custom mimtype config
        if conf:
            for mimetype, plugin in conf.items():
                self._mimetypes[mimetype] = plugin

    def have(self, mimetype):
        '''Returns TRUE if parser for mimetype exists, FALSE otherwise'''

        return mimetype in self._mimetypes

    def get(self, mimetype):
        '''Returns a suitable parser plugin for the given mimetype and extension'''

        if mimetype:
            # look for direct mimetype match
            if mimetype in self._mimetypes:
                return self._parser_factory(self._mimetypes[mimetype])

    def _parser_factory(self, key):
        '''Create a parser object'''

        try:
            conf = self._parserconf[key]
        except Exception:
            conf = {}

        return self._parsers[key](conf)
