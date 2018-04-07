from . import plugins
import hashlib
import datetime
from io import BytesIO
import mimetypes
import os
import urllib.parse
import urllib.request
import logging


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
                self._backend.update(id, self.last_seen())
                continue

            if self.ignore_file(file):
                continue

            self._logger.add(file.url + ' (' + str(file.mimetype) + ')')

            try:
                document = self.prepare_document(file, conf)
            except Exception as e:
                logging.exception(e)
                continue

            if backend_document:
                self._backend.update(id, document)
            else:
                self._backend.create(id, document)

        self._logger.add('Purging removed files from index...')
        self._backend.remove_seen_older_than(self._datetime_to_epoch(start_time))

    def backend_document(self, id, sourcename):
        return self._backend.get(id, sourcename)

    def modified(self, file, backend_document):
        if file.modified and backend_document['modified'] and (file.modified <= backend_document['modified']):
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
            'title': file.title,
            'url': file.url,
            'extension': file.extension,
            'mimetype': file.mimetype,
            'created': file.created,
            'modified': file.modified,
            'size': file.size,
            'read_allowed': file.read_allowed,
            'read_denied': file.read_denied
        }

        parsed_content = ''
        filetype_metadata = {}

        if self._parsers.have(file.mimetype):
            try:
                parsed_content, filetype_metadata = self.parse_content(file)
            except Exception as e:
                logging.exception(e)
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
        document['last_seen'] = datetime.datetime.now()

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


def path2url(path, protocol='file'):
    '''Turns filesystem path into url with file: protocol'''
    return urllib.parse.urljoin(protocol + ':', urllib.request.pathname2url(path))


class File(object):

    title = None
    url = None
    created = None
    modified = None
    size = None

    read_allowed = []
    read_denied = []

    _mimetype = None

    @property
    def extension(self):
        return os.path.splitext(self.url)[1].strip('.')

    @property
    def mimetype(self):
        if self._mimetype:
            return self._mimetype

        return mimetypes.guess_type(self.url)[0]

    @mimetype.setter
    def mimetype(self, mimetype):
        self._mimetype = mimetype


class LocalFile(File):

    # The full local file path
    path = None

    def __init__(self, path):
        super().__init__()

        self.path = path
        self._set_properties(path)

    def open(self):
        return open(self.path, mode='rb')

    def _set_properties(self, path):
        statdata = os.stat(path)

        self.title = os.fsdecode(os.path.splitext(os.path.basename(path))[0])
        self.url = path2url(os.fsdecode(path))
        self.created = datetime.datetime.fromtimestamp(statdata.st_ctime)
        self.modified = datetime.datetime.fromtimestamp(statdata.st_mtime)
        self.size = statdata.st_size


class MemoryFile(File):

    _contents = ''

    def __init__(self, contents):
        super().__init__()
        self._contents = contents

    def open(self):
        return BytesIO(self._contents)


class NoParserFoundException(Exception):
    pass
