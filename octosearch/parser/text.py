
class ParserText(object):
    def __init__(self, conf):
        pass

    def types(self):
        return ['text/plain', 'text/markdown']

    def parse(self, file):
        '''Dump file contents straight back to indexer'''

        with file.open() as f:
            content = f.read()

        return content.decode('utf-8')

    def extra(self):
        return {}
