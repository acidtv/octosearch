import httplib
import json
import math

class OutputElasticSearch:

    server = None

    index = None

    def __init__(self, server, index):
        self.server = server
        self.index = index

    def add(self, id, info):
        """Add new document to index"""

        result = self._es_call('put', '/' + self.index + '/document/' + id, info)

    def get_all(self):
        '''Generator. Returns the entire index'''

        result = self._es_call('get', '/' + self.index + '/document/_search?path:*', None)

        pagesize = 100
        pages = int(math.ceil(result['hits']['total']/(pagesize+.0)))

        for page in range(pages):
            pagefrom = (pagesize*page)
            url = '/' + self.index + '/document/_search?path:*&fields=path,filename&from=' + str(pagefrom) + '&size=' + str(pagesize)
            result = self._es_call('get', url, None)

            for document in self._format_results(result):
                yield document

    def get_keys(self, keys):
        '''Returns list with specified keys'''

        query = {
                'size': 100000,
                'fields': ['id', 'path', 'filename', 'created', 'modified', 'mimetype'],
                'query': { 'ids': {'values': keys} }
                }

        result = self._es_call('get', '/' + self.index + '/document/_search', query)

        return self._format_results(result)

    def remove(self, files):
        '''Remove files from index'''

        query = {'ids': {'values': files}}
        self._es_call('delete', '/' + self.index + '/document/_query', query)

    def truncate(self):
        '''Empty the entire index'''

        self._es_call('delete', '/' + self.index + '/document')

    def _format_results(self, results):
        '''Generator. Normalize elastic search results'''

        if not 'hits' in results:
            return

        for document in results['hits']['hits']:
            dump = {
                    'id': document['_id'],
                    'path': document['fields'].get('path'),
                    'filename': document['fields'].get('filename'),
                    'created': document['fields'].get('created'),
                    'modified': document['fields'].get('modified'),
                    'mimetype': document['fields'].get('mimetype')
                    }

            yield dump

    def _es_call(self, method, url, content=None):
        '''Call elastic search server'''

        jsondoc = ''
        method = method.upper()

        if content:
            jsondoc = json.dumps(content)

        httpcon = httplib.HTTPConnection(self.server, 9200)
        httpcon.request(method, url, jsondoc, {'Content-type': 'application/json'})
        response = httpcon.getresponse()

        jsondoc = json.loads(response.read())

        httpcon.close()

        return jsondoc

