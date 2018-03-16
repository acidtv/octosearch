import plugins
import hashlib
import datetime
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
        start_time = datetime.datetime.now()

        if 'ignore-extensions' in conf:
            self.ignore_extensions = conf['ignore-extensions']

        for file in indexer.index(conf):
            metadata = file.metadata()
            id = self.file_id(metadata)
            backend_document = self.backend_document(id, conf['name'])

            if backend_document and not self.modified(metadata, backend_document):
                self.logger.add(metadata['url'] + ' not modified, updating last seen date')
                self.backend.add(id, self.last_seen())

            elif not self.ignore_file(metadata):
                self.logger.add(metadata['url'] + ' (' + str(metadata['mimetype']) + ')')

                try:
                    document = self.prepare_document(file, conf)
                except NoParserFoundException as e:
                    self.logger.add('Skipping file %s: %s' % (metadata['url'], str(e)))
                    continue
                except Exception as e:
                    self.logger.add('Could not prepare document for storage %s: %s' % (file, e))
                    continue

                self.backend.add(id, document)

        self.logger.add('Purging removed files from index...')
        self.backend.remove_seen_older_than(self._datetime_to_epoch(start_time))

    def backend_document(self, id, sourcename):
        backend_document = None

        try:
            backend_document = self.backend.get_keys([id], sourcename).next()
        except StopIteration:
            pass
        finally:
            return backend_document

    def modified(self, metadata, backend_document):
        if metadata['modified'] <= backend_document['modified']:
            return False

        return True

    def ignore_file(self, metadata):
        if metadata['extension'] in self.ignore_extensions:
            return True

        if metadata['mimetype'] in self.ignore_mimetypes:
            return True

        return False

    def file_id(self, metadata):
        return hashlib.md5(metadata['url']).hexdigest()

    def prepare_document(self, file, conf):
        mimetype = file.metadata()['mimetype']

        if not self.parsers.have(mimetype):
            raise NoParserFoundException('No parser found for mimetype %s' % mimetype)

        parsed_content, filetype_metadata = self.parse_content(file)

        # prepare for adding to backend
        document = file.metadata()
        document['sourcename'] = conf['name']
        document['content'] = parsed_content
        document['last_seen'] = self.last_seen()['last_seen']

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
        parser = self.parsers.get(metadata['mimetype'])

        content = parser.parse(file)

        if not isinstance(content, str) and not isinstance(content, unicode):
            raise Exception('Parser must return string')

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
