import os
import os.path

from ...indexer import LocalFile


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

                yield LocalFile(full_path)

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
