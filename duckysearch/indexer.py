import plugins
import hashlib


class Indexer(object):

    logger = None

    indexer = None

    backend = None

    parsers = None

    ignore_extensions = []

    ignore_mimetypes = []

    def index(self, conf):
        indexer = plugins.get('indexer', conf['indexer'])()

        for metadata in indexer.index(conf):
            id = self.file_id(metadata)
            if not self.ignore_file(id, metadata, conf['name']):
                self.logger.add(metadata['url'] + ' (' + str(metadata['mimetype']) + ')')
                document = self.prepare_document(
                    metadata,
                    self.get_file_content(indexer, metadata),
                    conf['name']
                )
                self.backend.add(id, document)

    def ignore_file(self, id, metadata, sourcename):
        # FIXME query a bunch of ids at the same time, instead of doing a query for every file
        try:
            backend_document = self.backend.get_keys([id], sourcename).next()

            if metadata['modified'] <= backend_document['modified']:
                return True
        except StopIteration:
            pass

        if metadata['extension'] in self.ignore_extensions:
            return True

        if metadata['mimetype'] in self.ignore_mimetypes:
            return True

        return False

    def get_file_content(self, indexer, metadata):
        if 'content' in metadata:
            return metadata['content']

        return indexer.get_file_content(metadata)

    def file_id(self, metadata):
        return hashlib.md5(metadata['url']).hexdigest()

    def prepare_document(self, metadata, content, sourcename):
        parsed_content, filetype_metadata = self.parse_content(
            content,
            metadata,
        )

        # prepare for adding to backend
        document = metadata
        document['sourcename'] = sourcename
        document['content'] = parsed_content
        document['filetype_metadata'] = filetype_metadata

        return document

    def parse_content(self, content, metadata):
        parser = self._plugins.get(metadata['mimetype'], metadata['extension'])

        content = parser.parse(content, metadata)

        if not isinstance(content, str):
            raise Exception('Parser must return string')

        # get metadata based on filetype, like image dimensions or compression ratio
        filetype_metadata = parser.extra()

        if not isinstance(filetype_metadata, dict):
            raise Exception('Extra info from parser must be dict')

        return content, filetype_metadata
