import http.client
import json


class BackendElasticSearch:

    server = None

    index = None

    # user groups to filter on
    _user_groups = None
    _user_auth = None

    _last_error = None

    _document_type = 'document'

    _default_sort = [
        {'_score': 'desc'},
        {'_id': 'asc'}
    ]

    _page_size = 10

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

    def auth(self, auth, groups):
        if not isinstance(groups, list):
            raise Exception('groups param must be a list')

        self._user_auth = auth
        self._user_groups = groups

    def search(self, query_str, auth=None, page=1):
        query = {
                '_source': ['id', 'path', 'filename', 'created', 'modified', 'mimetype', 'url', 'title'],
                'highlight': {
                    'fields': {
                        'content': {}
                        }
                    },
                'query': {
                    'bool': {
                        'must': {
                            'multi_match': {
                                'query': query_str,
                                'fields': ['content', 'url']
                                },
                            },
                        }
                    },
                'sort': self._default_sort
                }

        if not self._user_auth:
            # only show results that don't need authentication when user not authenticated
            query['query']['bool'].update({
                'filter': [
                    {'term': {'auth': ''}}
                    ]
                })
        elif self._user_auth is not None:
            # also show non-authenticated results when user *is* authenticated
            query['query']['bool']['filter'] = {
                'bool': {
                    'should': [
                        {'term': {'auth': ''}}
                    ]
                }
            }

            if self._user_groups is not None:
                # show authenticated results that user is allowed to read according to the _user_groups
                query['query']['bool']['filter']['bool']['should'].append({
                    'bool': {
                        'must': [
                            {'term': {'auth': self._user_auth}},
                            {'terms': {'read_allowed': self._user_groups}}
                        ]
                    }
                })

                # do not show results for which users access is denied
                query['query']['bool'].update({
                    'must_not': {
                        'terms': {
                            'read_denied': self._user_groups
                            }
                        }
                    })

        query['from'] = (page - 1) * self._page_size
        query['size'] = self._page_size

        result = self._es_call('get', '/' + self.index + '/_search', query)

        return {
            'hits': list(self._format_results(result)),
            'found': result['hits']['total']
        }

    def get_all(self):
        '''Generator. Returns the entire index'''

        # FIXME use elastic scrolling feature?
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

    def remove_seen_older_than(self, seen):
        '''Remove documents where last_seen is older than seen'''

        query = {
                'query': {
                    'range': {
                        'last_seen': {'lt': seen}
                        }
                    }
                }

        self._es_call('post', '/' + self.index + '/_delete_by_query', query)

    def _format_results(self, results):
        '''Generator. Normalize elastic search results'''

        if 'hits' not in results:
            return

        for document in results['hits']['hits']:
            dump = {
                    'id': document['_id'],
                    'score': document['_score'],
                    'path': document['_source'].get('path'),
                    'filename': document['_source'].get('filename'),
                    'title': document['_source'].get('title'),
                    'url': document['_source'].get('url'),
                    'created': document['_source'].get('created'),
                    'modified': document['_source'].get('modified'),
                    'mimetype': document['_source'].get('mimetype'),
                    }

            # not all results have highlights
            if 'highlight' in document:
                dump['highlight'] = document['highlight'].get('content')

            yield dump

    def _set_mapping(self):
        mapping = {
            "mappings": {
                self._document_type: {
                    "properties": {
                        "title": {
                            "type": "text",
                            },
                        "content": {
                            "type": "text",
                            },
                        "url": {
                            "type": "text",
                            },
                        "read_allowed": {
                            "type": "keyword",
                            "index": True,
                            },
                        "read_denied": {
                            "type": "keyword",
                            "index": True,
                            },
                        "sourcename": {
                            "type": "keyword",
                            "index": True,
                            },
                        "auth": {
                            "type": "keyword",
                            "index": True,
                            },
                        "created": {
                            "type": "date",
                            },
                        "modified": {
                            "type": "date",
                            },
                        "last_seen": {
                            "type": "date",
                            },

                        # text / keyword fields for search flexibility
                        "filename": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    }
                                }
                            },
                        "mimetype": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    }
                                }
                            },
                        "path": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    }
                                }
                            },
                        }
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

        httpcon = http.client.HTTPConnection(self.server, 9200)
        httpcon.request(method, url, jsondoc, {'Content-type': 'application/json'})
        response = httpcon.getresponse()

        jsondoc = json.loads(str(response.read(), encoding='utf-8'))

        httpcon.close()

        if self._is_error(jsondoc):
            self._last_error = jsondoc
            raise ElasticRequestError(self._get_error_desc(jsondoc))

        return jsondoc

    def _is_error(self, result):
        return True if 'error' in result else False

    def _get_error_desc(self, result):
        return result['error']['root_cause'][0]['reason']

    def default_sort(self):
        return self._default_sort

    def pagesize(self):
        return self._page_size


class ElasticRequestError(Exception):
    pass
