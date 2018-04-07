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

            for file in os.listdir(path):
                full_path = os.path.join(path, file)

                # if dir add to stack
                if os.path.isdir(full_path):
                    dirstack.append(full_path)
                    continue

                try:
                    yield LocalFile(full_path)
                except Exception as e:
                    logging.exception(e)

                    logging.info('Trying to index only the filename for {}', full_path)
                    memfile = MemoryFile('')
                    memfile.url = path2url(os.fsdecode(full_path))
                    memfile.path = full_path

                    yield memfile
