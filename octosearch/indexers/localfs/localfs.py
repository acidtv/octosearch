import os
import os.path

from ...indexer import LocalFile


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

                yield LocalFile(full_path)
