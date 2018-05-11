from . import plugins
import hashlib
import datetime
from io import BytesIO
import mimetypes
import os
import urllib.parse
import urllib.request
import logging
import itertools


class Indexer(object):

    _backend = None

    _parsers = None

    ignore_mimetypes = []

    ingest_batch_size = 100

    def __init__(self, backend, parsers):
        self._backend = backend
        self._parsers = parsers

    def index(self, conf):
        indexer = plugins.get('indexer', conf['indexer'])()
        start_time = datetime.datetime.now()

        documents = self._walk_documents(indexer.index(conf), conf)
        self._backend.bulk(documents)

        logging.info('Purging removed files from index...')
        self._backend.remove_seen_older_than(self._datetime_to_epoch(start_time))

    def _walk_documents(self, files, conf):
        for files_ids in self._group_files_ids(files, self.ingest_batch_size, conf):
            for id, file, backend_document in files_ids:
                if self.ignore_file(file):
                    continue

                action = 'update' if backend_document else 'create'

                try:
                    document = self.prepare_document(file, conf, backend_document)
                    job = (id, action, document)
                except Exception as e:
                    logging.exception(e)
                    continue

                logging.info(job[1] + ' ' + file.url + ' (' + str(file.mimetype) + ')')

                yield job

    def _group_files_ids(self, files, size, conf):
        for slice in iter(lambda: list(itertools.islice(files, size)), []):
            # set up basic return dict with file-id and file object
            files_ids = dict([(self.file_id(file), [file, None]) for file in slice])

            # add existing docs
            for doc in self._backend.get(list(files_ids.keys()), conf['name']):
                files_ids[doc['id']][1] = doc

            # format and yield
            yield ([item[0]] + item[1] for item in files_ids.items())

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

    def prepare_document(self, file, conf, backend_document):
        document = {
            'title': file.title,
            'url': file.url,
            'extension': file.extension,
            'mimetype': file.mimetype,
            'created': file.created,
            'modified': file.modified,
            'size': file.size,
            'read_allowed': file.read_allowed,
            'read_denied': file.read_denied,
            'sourcename': conf['name'],
            'last_seen': datetime.datetime.now(),
        }

        # Parse content if the document is not in the backend yet (new file) or the file is modified,
        if (not backend_document) or self.modified(file, backend_document):
            if self._parsers.have(file.mimetype):
                try:
                    document['content'], document['filetype_metadata'] = self.parse_content(file)

                    # If parser extracted a title, add that to the document
                    if 'title' in document['filetype_metadata'] and not file.title:
                        document['title'] = document['filetype_metadata']['title']
                except Exception as e:
                    logging.exception(e)
            else:
                logging.info('No parser found for  %s' % file.url)

        document['auth'] = ''

        if 'auth' in conf:
            document['auth'] = conf['auth']

        return document

    def parse_content(self, file):
        parser = self._parsers.get(file.mimetype)

        try:
            content = parser.parse(file)
        except PermissionError:
            logging.error('Permission denied while trying to parse %s, so we\'re not indexing the contents.', file.url)
            return '', {}

        if not isinstance(content, str):
            raise Exception('Parser must return type `unicode`')

        # get metadata based on filetype, like image dimensions or compression ratio
        filetype_metadata = parser.extra()

        if not filetype_metadata:
            filetype_metadata = {}

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
