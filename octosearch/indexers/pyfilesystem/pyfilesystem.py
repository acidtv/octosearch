from fs import open_fs
from fs.walk import Walker

from ...indexer import File


class Pyfilesystem(object):

    def index(self, conf):
        fs = open_fs(conf['url'])
        walker = Walker()

        for path in walker.files(fs):
            yield Pyfsfile(fs, path)


class Pyfsfile(File):

    path = None

    def __init__(self, fs, path):
        super().__init__()

        self.path = path
        self.fs = fs

    def open(self):
        return self.fs.openbin(self.path)
