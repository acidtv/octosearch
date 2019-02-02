from . import plugins


class ParserPlugins(object):

    _parsers = {
            'mimetypes': {},
            }

    _parserconf = {}

    def __init__(self, conf, parserconf):
        """Load parsers to see which mimetypes they want
            to take care of"""

        self._parserconf = parserconf

        # load parsers registered with setuptools
        for plugin in plugins.list('parser'):
            self._parsers['mimetypes'][plugin.name] = (plugin.name, plugin.load())

        # add custom mimtype config
        if conf:
            for mimetype, plugin in conf.items():
                self._parsers['mimetypes'][mimetype] = (plugin, plugins.get('parser', plugin))

    def have(self, mimetype):
        '''Returns TRUE if parser for mimetype exists, FALSE otherwise'''

        return mimetype in self._parsers['mimetypes']

    def get(self, mimetype):
        '''Returns a suitable parser plugin for the given mimetype and extension'''

        if mimetype:
            # look for direct mimetype match
            if mimetype in self._parsers['mimetypes']:
                return self._parser_factory('mimetypes', mimetype)

    def _parser_factory(self, parsertype, key):
        try:
            conf = self._parserconf[self._parsers[parsertype][key][0]]
        except Exception as e:
            conf = {}

        return self._parsers[parsertype][key][1](conf)
