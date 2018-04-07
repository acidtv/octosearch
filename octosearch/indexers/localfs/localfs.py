import os
import os.path
import logging

from ...indexer import LocalFile, MemoryFile, path2url


class Localfs(object):

    def index(self, conf):
        """Index a directory"""

        # encode to bytes, because that's what the filesystem uses
        path = os.fsencode(conf['path'])

        dirstack = [path]

        # walk filesystem
        while dirstack:
            path = dirstack.pop()
            files = []

            try:
                files = os.listdir(path)
            except PermissionError as e:
                logging.error('Could not access %s, skipping', path)

            for file in files:
                full_path = os.path.join(path, file)

                # if dir add to stack
                if os.path.isdir(full_path):
                    dirstack.append(full_path)
                    continue

                try:
                    yield LocalFile(full_path)
                except Exception as e:
                    logging.exception(e)
                    logging.info('Trying to index only the filename for %s', full_path)
                    yield self._simple_file(full_path)

    def _simple_file(self, path):
        '''Returns a MemoryFile object with only the path and url'''
        memfile = MemoryFile(b'')
        memfile.url = path2url(os.fsdecode(path))
        memfile.path = path

        return memfile
