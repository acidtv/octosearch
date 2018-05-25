import elasticsearch
from elasticsearch_dsl import Search, Q, Index, DocType, Text, Keyword, Date, connections
import time
import datetime


class BackendElasticSearch:

    _server = None

    _index_name = None

    # user groups to filter on
    _user_groups = None
    _user_auth = None

    _default_sort = [
        {'_score': 'desc'},
        {'_id': 'asc'}
    ]

    _page_size = 10

    _bulk_chunk_size = 100

    def __init__(self, server, index):
        self._server = server
        self._index_name = index

        connections.create_connection(hosts=[self._server])

        self._init_index()

    def _index(self):
        return Index(name=self._index_name)

    def _search(self):
        return Document.search(index=self._index_name)

    def _document(self, id=None, **values):
        doc = Document(**values)
        doc.meta.index = self._index_name

        if id:
            doc.meta.id = id

        return doc

    def _init_index(self):
        '''Check if index exists, if not create it and set the field mapping'''
        elastic_index = self._index()
        elastic_index.doc_type(Document)
        elastic_index.create(ignore=400)

    def create(self, id, info):
        """Add new document to index"""
        self._document(id, **info).save()

    def update(self, id, info):
        """Update a document in the index"""
        self._document(id).update(**info)

    def bulk(self, documents):
        """Takes a documents generator, converts to ES format and passes generator on to ES bulk call"""

        conn = connections.get_connection()

        for result in elasticsearch.helpers.streaming_bulk(
            client=conn,
            actions=self._bulk_generator(documents),
            chunk_size=self._bulk_chunk_size,
        ):
            pass

    def _bulk_generator(self, documents):
        """Yields actions for bulk requests from documents"""
        for id, action, document in documents:
            yield self._bulk_doc_to_dict(id, action, document)

    def _bulk_doc_to_dict(self, id, action, document):
        document_dict = self._document(id, **document).to_dict(include_meta=True)

        if action == 'update':
            # set operation type to update, otherwise document is replaced with only
            # the 'last_seen' field
            document_dict['_op_type'] = 'update'

            # update action requires fields to be in 'doc' key, not in '_source'
            document_dict['doc'] = document_dict['_source']
            del document_dict['_source']

        return document_dict

    def auth(self, auth, groups):
        if not isinstance(groups, list):
            raise Exception('groups param must be a list')

        self._user_auth = auth
        self._user_groups = groups

    def search(self, query_str, auth=None, page=1):
        s = self._search()

        s = s.source(['id', 'path', 'filename', 'created', 'modified', 'mimetype', 'url', 'title'])
        s = s.highlight('content')

        s = s.query("simple_query_string", query=query_str, fields=['title^2', 'content', 'url'], default_operator="and")

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
        s = s[page_from:page_from+self._page_size]

        # FIXME is sorting needed?
        # 'sort': self._default_sort

        response = s.execute()

        return {
            'hits': self._formatted_hits(response),
            'found': response.hits.total
        }

    def _formatted_hits(self, response):
        for hit in response:
            formatted_hit = {
                'id': hit.meta.id,
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

    def get(self, ids, sourcename):
        s = self._document().search()

        s = s.source(['id', 'path', 'filename', 'created', 'modified', 'mimetype', 'url', 'title'])
        s = s.filter(Q('ids', values=ids) & Q('term', sourcename=sourcename))

        # ES returns pages of 10 by default, so set limit to amount of ids.
        # In case this gets too much for ES we should switch to scanning/scrolling
        s = s[0:len(ids)]
        response = s.execute()

        if response.hits.total == 0:
            return []

        return self._formatted_hits(response)

    def truncate(self):
        '''Empty the entire index'''
        self._index().delete()

    def remove_seen_older_than(self, seen):
        '''Remove documents where last_seen is older than seen'''

        # Give ES some time to process 'last_seen' updates
        # FIXME: See if we can do better than adding a sleep() here
        time.sleep(2)

        s = self._search().query(Q('range', last_seen={'lt': seen}))
        s.delete()

    def pagesize(self):
        return self._page_size


class Document(DocType):

    title = Text()
    content = Text()

    # Use simple analyzer, so every part of the url will be a term, including the extension.
    # The path_hierarchy might be useful too, see https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-pathhierarchy-tokenizer.html
    url = Text(analyzer='simple')

    read_allowed = Keyword(multi=True)
    read_denied = Keyword(multi=True)
    sourcename = Keyword()
    auth = Keyword()

    created = Date()
    modified = Date()
    last_seen = Date()

    filename = Text(fields={'keyword': Keyword()})
    mimetype = Text(fields={'keyword': Keyword()})
    path = Text(fields={'keyword': Keyword()})
