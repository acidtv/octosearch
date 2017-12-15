import httplib
import json
import math

class BackendElasticSearch:

    server = None

    index = None

    # user groups to filter on
    _user_groups = None

    def __init__(self, server, index):
        self.server = server
        self.index = index


    def add(self, id, info):
        """Add new document to index"""

        result = self._es_call('put', '/' + self.index + '/document/' + id, info)

    def permissions(self, groups):
        if not isinstance(groups, list):
            raise Exception('groups param must be a list')

        self._user_groups = groups

    def search(self, query_str):
        query = {
                'query': {
                    'bool': {
                        'must': {
                            'match': {
                                'content': query_str
                                },
                            },
                        }
                    }
                }

        if self._user_groups is not None:
            query['query']['bool'].update({
                'filter': {
                    'must': {
                        'terms': {
                            'read_allowed': self._user_groups
                            }
                        },
                    'must_not': {
                        'terms': {
                            'read_denied': self._user_groups
                            }
                        }
                    }
                })

        result = self._es_call('get', '/' + self.index + '/_search', query)

        for document in self._format_results(result):
            yield document

    def get_all(self):
        '''Generator. Returns the entire index'''

        result = self._es_call('get', '/' + self.index + '/_search', None)
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
                    'path': document['_source'].get('path'),
                    'filename': document['_source'].get('filename'),
                    'created': document['_source'].get('created'),
                    'modified': document['_source'].get('modified'),
                    'mimetype': document['_source'].get('mimetype')
                    }

            yield dump

    def _set_mapping(self, index):
        mapping = {
           'document': {
               "properties": {
                   "read_allowed": {
                       "type": "keyword",
                       "index": True,
                       },
                   "read_denied": {
                       "type": "keyword",
                       "index": True,
                       },
                   },
               },
           }

        return self._es_call('PUT', '/' + self.index + '/_mapping/document', mapping)

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

