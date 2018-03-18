import plugins
import hashlib
import datetime
from io import BytesIO, StringIO


class Indexer(object):

    _logger = None

    _backend = None

    _parsers = None

    ignore_mimetypes = []

    def __init__(self, logger, backend, parsers):
        self._logger = logger
        self._backend = backend
        self._parsers = parsers

    def index(self, conf):
        indexer = plugins.get('indexer', conf['indexer'])()
        start_time = datetime.datetime.now()

        for file in indexer.index(conf):
            metadata = file.metadata()
            id = self.file_id(metadata)
            backend_document = self.backend_document(id, conf['name'])

            if backend_document and not self.modified(metadata, backend_document):
                self._logger.add(metadata['url'] + ' not modified, updating last seen date')
                self._backend.add(id, self.last_seen())

            elif not self.ignore_file(metadata):
                self._logger.add(metadata['url'] + ' (' + str(metadata['mimetype']) + ')')

                try:
                    document = self.prepare_document(file, conf)
                except Exception as e:
                    self._logger.add('Could not prepare document for storage %s: %s' % (file, e))
                    continue

                self._backend.add(id, document)

        self._logger.add('Purging removed files from index...')
        self._backend.remove_seen_older_than(self._datetime_to_epoch(start_time))

    def backend_document(self, id, sourcename):
        backend_document = None

        try:
            backend_document = self._backend.get_keys([id], sourcename).next()
        except StopIteration:
            pass
        finally:
            return backend_document

    def modified(self, metadata, backend_document):
        if metadata['modified'] <= backend_document['modified']:
            return False

        return True

    def ignore_file(self, metadata):
        if metadata['mimetype'] in self.ignore_mimetypes:
            return True

        return False

    def file_id(self, metadata):
        return hashlib.md5(metadata['url']).hexdigest()

    def prepare_document(self, file, conf):
        document = file.metadata()
        parsed_content = u''
        filetype_metadata = {}

        if self._parsers.have(document['mimetype']):
            parsed_content, filetype_metadata = self.parse_content(file)
        else:
            self._logger.add('No parser found for  %s' % document['url'])

        # prepare for adding to backend
        document['sourcename'] = conf['name']
        document['last_seen'] = self.last_seen()['last_seen']
        document['content'] = parsed_content
        # file type specific metadata
        document['filetype_metadata'] = filetype_metadata

        if 'title' in filetype_metadata and 'title' not in file.metadata():
            document['title'] = filetype_metadata['title']

        document['auth'] = ''

        if 'auth' in conf:
            document['auth'] = conf['auth']

        return document

    def last_seen(self):
        document = {}
        document['last_seen'] = self._datetime_to_epoch(datetime.datetime.now())

        return document

    def parse_content(self, file):
        metadata = file.metadata()
        parser = self._parsers.get(metadata['mimetype'])

        content = parser.parse(file)

        if not isinstance(content, unicode):
            raise Exception('Parser must return type `unicode`')

        # get metadata based on filetype, like image dimensions or compression ratio
        filetype_metadata = parser.extra()

        if not isinstance(filetype_metadata, dict):
            raise Exception('Extra info from parser must be dict')

        return content, filetype_metadata

    def _datetime_to_epoch(self, dt):
        return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


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
        return open(self._path, mode='rt')


class MemoryFile(File):

    _contents = ''

    def __init__(self, contents, metadata, encoding=None):
        self._contents = contents
        super(MemoryFile, self).__init__(metadata, encoding)

    def open_binary(self):
        return BytesIO(self._contents)

    def open_text(self):
        return StringIO(self._contents)


class NoParserFoundException(Exception):
    pass
