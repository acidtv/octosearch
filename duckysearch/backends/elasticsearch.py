import httplib
import json


class BackendElasticSearch:

    server = None

    index = None

    # user groups to filter on
    _user_groups = None

    _last_error = None

    _document_type = 'document'

    def __init__(self, server, index):
        self.server = server
        self.index = index

        self.init_index(index)

    def init_index(self, index):
        '''Check if index exists, if not create it and set the field mapping'''

        try:
            self._es_call('get', '/' + index)
        except ElasticRequestError as e:
            if self._last_error['status'] != 404:
                raise e

            self._set_mapping()

    def add(self, id, info):
        """Add new document to index"""

        document = {
                'doc': info,
                'doc_as_upsert': True,
                }

        # execute upsert
        self._es_call('post', '/' + self.index + '/' + self._document_type + '/' + id + '/_update', document)

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
                    'terms': {
                        'read_allowed': self._user_groups
                    }
                },
                'must_not': {
                    'terms': {
                        'read_denied': self._user_groups
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

    def get_keys(self, keys, sourcename):
        '''Returns list with specified keys'''

        query = {
                '_source': ['id', 'path', 'filename', 'created', 'modified', 'mimetype'],
                'query': {
                    'bool': {
                        'filter': [
                            {'ids': {'type': self._document_type, 'values': keys}},
                            {'term': {'sourcename': sourcename}}
                            ]
                        }
                    }
                }

        try:
            result = self._es_call('get', '/' + self.index + '/' + self._document_type + '/_search', query)
        except ElasticRequestError as e:
            # if index doesnt exist we get a 404
            if self._last_error['status'] == 404:
                return []

            raise e

        return self._format_results(result)

    def remove(self, files):
        '''Remove files from index'''

        query = {'ids': {'values': files}}
        self._es_call('delete', '/' + self.index + '/' + self._document_type + '/_query', query)

    def truncate(self):
        '''Empty the entire index'''

        self._es_call('delete', '/' + self.index)

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

    def _set_mapping(self):
        mapping = {
            "mappings": {
                self._document_type: {
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
                    }
                }
           }

        self._es_call('PUT', '/' + self.index, mapping)

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

        if self._is_error(jsondoc):
            self._last_error = jsondoc
            raise ElasticRequestError(self._get_error_desc(jsondoc))

        return jsondoc

    def _is_error(self, result):
        return True if 'error' in result else False

    def _get_error_desc(self, result):
        return result['error']['root_cause'][0]['reason']


class ElasticRequestError(Exception):
    pass
