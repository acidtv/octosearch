from . import plugins
import hashlib
import datetime
from io import BytesIO
import mimetypes
import os
import urllib.parse
import urllib.request


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
            id = self.file_id(file)
            backend_document = self.backend_document(id, conf['name'])

            if backend_document and not self.modified(file, backend_document):
                self._logger.add(file.url + ' not modified, updating last seen date')
                self._backend.add(id, self.last_seen())

            elif not self.ignore_file(file):
                self._logger.add(file.url + ' (' + str(file.mimetype) + ')')

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
            backend_document = next(self._backend.get_keys([id], sourcename))
        except StopIteration:
            pass
        finally:
            return backend_document

    def modified(self, file, backend_document):
        if file.modified <= backend_document['modified']:
            return False

        return True

    def ignore_file(self, file):
        if file.mimetype in self.ignore_mimetypes:
            return True

        return False

    def file_id(self, file):
        return hashlib.md5(file.url.encode()).hexdigest()

    def prepare_document(self, file, conf):
        document = {
            'filename': file.filename,
            'path': file.path,
            'url': file.url,
            'extension': file.extension,
            'mimetype': file.mimetype,
            'created': file.created,
            'modified': file.modified,
            'size': file.size
        }

        parsed_content = ''
        filetype_metadata = {}

        if self._parsers.have(file.mimetype):
            parsed_content, filetype_metadata = self.parse_content(file)
        else:
            self._logger.add('No parser found for  %s' % file.url)

        # prepare for adding to backend
        document['sourcename'] = conf['name']
        document['last_seen'] = self.last_seen()['last_seen']
        document['content'] = parsed_content
        # file type specific metadata
        document['filetype_metadata'] = filetype_metadata

        if 'title' in filetype_metadata and not file.title:
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
        parser = self._parsers.get(file.mimetype)

        content = parser.parse(file)

        if not isinstance(content, str):
            raise Exception('Parser must return type `unicode`')

        # get metadata based on filetype, like image dimensions or compression ratio
        filetype_metadata = parser.extra()

        if not isinstance(filetype_metadata, dict):
            raise Exception('Extra info from parser must be dict')

        return content, filetype_metadata

    def _datetime_to_epoch(self, dt):
        return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


class File(object):

    filename = None
    path = None
    url = None
    extension = None
    mimetype = None
    created = None
    modified = None
    size = None

    def __init__(self, filename=None, path=None, url=None, extension=None, mimetype=None, created=None, modified=None, size=None, read_allowed=None, read_denied=None):
        self.filename = filename
        self.path = path
        self.url = url
        self.extension = extension
        self.mimetype = mimetype
        self.created = created
        self.modified = modified
        self.size = size
        self.read_allowed = read_allowed
        self.read_denied = read_denied


class LocalFile(File):

    def __init__(self, filename):
        super().__init__(**kwargs)
        self._properties()

    def open(self):
        return open(self._path, mode='rb')

    def _properties(self, path, file):
        '''Index a file'''

        file_full = os.path.join(path, file)
        statdata = os.stat(file_full)

        return {
            filename = file
            path = path
            url = path2url(file_full)
            extension = self._get_extension(file)
            mimetype = self._get_mimetype(file)
            created = statdata.st_ctime
            modified = statdata.st_mtime
            size = statdata.st_size
        }

    def _get_extension(self, file):
        info = file.rpartition(os.extsep)

        if info[0] != '' and info[2] != '':
            return info[2]

        return ''

    def _get_mimetype(self, file):
        mimetype = mimetypes.guess_type(file.filename)[0]
        return mimetype


class MemoryFile(File):

    _contents = ''

    def __init__(self, contents, **kwargs):
        self._contents = contents
        super().__init__(**kwargs)

    def open(self):
        return BytesIO(self._contents)


class NoParserFoundException(Exception):
    pass


def path2url(path, protocol='file'):
    '''Turns filesystem path into url with file: protocol'''
    return urllib.parse.urljoin(protocol + ':', urllib.request.pathname2url(path))
