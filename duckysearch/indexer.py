import plugins
import hashlib
from io import BytesIO, StringIO


class Indexer(object):

    logger = None

    indexer = None

    backend = None

    parsers = None

    ignore_extensions = []

    ignore_mimetypes = []

    def index(self, conf):
        indexer = plugins.get('indexer', conf['indexer'])()

        if 'ignore-extensions' in conf:
            self.ignore_extensions = conf['ignore-extensions']

        for file in indexer.index(conf):
            metadata = file.metadata()
            id = self.file_id(metadata)
            if not self.ignore_file(id, metadata, conf['name']):
                self.logger.add(metadata['url'] + ' (' + str(metadata['mimetype']) + ')')
                document = self.prepare_document(file, conf)
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

    def file_id(self, metadata):
        return hashlib.md5(metadata['url']).hexdigest()

    def prepare_document(self, file, conf):
        parsed_content, filetype_metadata = self.parse_content(file)

        # prepare for adding to backend
        document = file.metadata()
        document['sourcename'] = conf['name']
        document['content'] = parsed_content
        document['filetype_metadata'] = filetype_metadata

        document['auth'] = ''

        if 'auth' in conf:
            document['auth'] = conf['auth']

        return document

    def parse_content(self, file):
        metadata = file.metadata()
        parser = self.parsers.get(metadata['mimetype'], metadata['extension'])

        content = parser.parse(file)

        if not isinstance(content, str) and not isinstance(content, unicode):
            raise Exception('Parser must return string')

        # get metadata based on filetype, like image dimensions or compression ratio
        filetype_metadata = parser.extra()

        if not isinstance(filetype_metadata, dict):
            raise Exception('Extra info from parser must be dict')

        return content, filetype_metadata


class File(object):

    _encoding = None

    _metadata = {}

    def __init__(self, metadata, encoding=None):
        self._metadata = metadata
        self._encoding = encoding

    def encoding(self):
        # FIXME if no encoding is set try to detect the file encoding
        return self._encoding

    def metadata(self):
        return self._metadata


class LocalFile(File):
    _path = None

    def __init__(self, path, metadata, encoding=None):
        self._path = path
        super(LocalFile, self).__init__(metadata, encoding)

    def open_binary(self):
        return open(self._path, mode='rb')

    def open_text(self):
        return open(self._path, mode='rt', encoding=self._encoding)


class MemoryFile(File):

    _contents = ''

    def __init__(self, contents, metadata, encoding=None):
        self._contents = contents
        super(MemoryFile, self).__init__(metadata, encoding)

    def open_binary(self):
        return BytesIO(self._contents)

    def open_text(self):
        return StringIO(self._contents)
