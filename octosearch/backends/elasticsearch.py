import http.client
import json
import elasticsearch
from elasticsearch_dsl import Search, Q, Index, DocType, Text, Keyword, Date


class BackendElasticSearch:

    server = None

    index = None

    _client = None

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
        self._client = elasticsearch.Elasticsearch(self.server + ':9200')

        self.init_index(index)

    def init_index(self, index_name):
        '''Check if index exists, if not create it and set the field mapping'''
        elastic_index = Index(index_name, using=self._client)
        elastic_index.doc_type(Document)
        elastic_index.create(ignore=400)

    def add(self, id, info):
        """Add new document to index"""
        doc = Document()
        doc.meta.id = id
        doc.update(using=self._client, index=self.index, doc_as_upsert=True, **info)

    def auth(self, auth, groups):
        if not isinstance(groups, list):
            raise Exception('groups param must be a list')

        self._user_auth = auth
        self._user_groups = groups

    def search(self, query_str, auth=None, page=1):
        s = Search(using=self._client)

        s = s.source(['id', 'path', 'filename', 'created', 'modified', 'mimetype', 'url', 'title'])
        s = s.highlight('content')

        s = s.query("multi_match", query=query_str, fields=['content', 'url'])

        query_empty_auth = Q('term', auth='')

        if not self._user_auth:
            s = s.filter(query_empty_auth)
        elif self._user_auth is not None:
            query_auth = Q('term', auth=self._user_auth)
            query_groups = Q('terms', read_allowed=self._user_groups)

            if self._user_groups is not None:
                s = s.filter(query_empty_auth | (query_groups & query_auth))
                s = s.exclude('terms', read_denied=self._user_groups)
            else:
                s = s.filter(query_empty_auth | query_auth)

        # paging
        page_from = (page - 1) * self._page_size
        page_size = self._page_size
        s = s[page_from:page_from+page_size]

        # FIXME is sorting needed?
        # 'sort': self._default_sort

        response = s.execute()

        return {
            'hits': list(self.formatted_hits(response)),
            'found': response.hits.total
        }

    def formatted_hits(self, response):
        for hit in response:
            formatted_hit = {
                'id': hit.meta.id,
                'score': hit.meta.score,
                'title': hit.title if 'title' in hit else '',
                'url': hit.url,
                'created': hit.created,
                'modified': hit.modified,
                'mimetype': hit.mimetype,
            }

            # not all results have highlights
            if 'highlight' in hit.meta:
                formatted_hit['highlight'] = hit.meta.highlight.content

            yield formatted_hit

    def get(self, id, sourcename):
        s = Search(using=self._client)
        s = s.source(['id', 'path', 'filename', 'created', 'modified', 'mimetype', 'url', 'title'])
        s = s.filter(Q('ids', values=[id]) & Q('term', sourcename=sourcename))

        response = s.execute()
        return next(self.formatted_hits(response))

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


class Document(DocType):

    title = Text()
    content = Text()
    url = Text()

    # FIXME: does Index=True still needs to be set?
    read_allowed = Keyword(multi=True)
    read_denied = Keyword(multi=True)
    sourcename = Keyword()
    auth = Keyword()

    created = Date()
    modified = Date()
    last_seen = Date()

    class Meta:
        index = 'octosearch'
