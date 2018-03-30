
class ParserText:
    def types(self):
        return {
            'expressions': ['text/*']
        }

    def parse(self, file_full, statdata):
        '''Dump file contents straight back to indexer'''

        with file.open() as f:
            content = f.read()

        return content.decode('utf-8')

    def extra(self):
        return {}
