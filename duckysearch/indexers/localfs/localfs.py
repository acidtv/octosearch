import os
import os.path
import mimetypes

from ..indexer import LocalFile

class Localfs(object):

    def index(self, conf):
        """Index a directory"""

        dirstack = [conf['path']]

        # walk filesystem
        while dirstack:
            path = dirstack.pop()

            for file in os.listdir(path):
                full_path = os.path.join(path, file)

                # if dir add to stack
                if os.path.isdir(full_path):
                    dirstack.append(full_path)
                    continue

                yield self.process_file(path, file)

    def process_file(self, path, file):
        '''Index a file'''

        file_full = os.path.join(path, file)

        mimetype = self._get_mimetype(file_full)
        extension = self._get_extension(file)
        statdata = os.stat(file_full)

        metadata = {}
        metadata['filename'] = file
        metadata['path'] = path
        metadata['url'] = file_full
        metadata['extension'] = extension
        metadata['mimetype'] = mimetype
        metadata['created'] = statdata.st_ctime
        metadata['modified'] = statdata.st_mtime
        metadata['size'] = statdata.st_size

        return LocalFile(file_full, metadata)

    def get_file_content(self, metadata):
        file_full = os.path.join(metadata['path'], metadata['filename'])
        with open(file_full, 'r') as file_stream:
            return file_stream.read()

    def check_removed(self):
        '''Check the index for removed files'''

        self._logger.add('Checking index for removed files...')

        removed = []
        documents = self._backend.get_all()

        for document in documents:
            file_full = os.path.join(document['path'], document['filename'])
            if not os.path.isfile(file_full):
                self._logger.add('Removed: ' + file_full)
                removed.append(document['id'])

        if removed:
            self._logger.add('Waiting for search engine to process removed files...')
            self._backend.remove(removed)

    def _get_extension(self, file):
        info = file.rpartition(os.extsep)

        if info[0] != '' and info[2] != '':
            return info[2]

        return ''

    def _get_mimetype(self, file):
        mimetype = mimetypes.guess_type(file)[0]
        return mimetype
