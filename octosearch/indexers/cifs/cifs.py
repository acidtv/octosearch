import smbc
import os
import datetime
from ...indexer import File
from ..mountedcifs.mountedcifs import parse_cifsace, acl_sids, filter_acl_read, ACE_ACCESS_ALLOWED, ACE_ACCESS_DENIED
from contextlib import contextmanager


class Cifs(object):

    DIRENT_TYPE_FILE = 8

    DIRENT_TYPE_DIR = 7

    _conf = None

    _context = None

    def index(self, conf):
        self._conf = conf
        self._context = smbc.Context(auth_fn=self.auth)

        dirstack = [conf['url']]

        while dirstack:
            url = dirstack.pop()

            for entry in self.get_dir_entries(url):
                entry_url = '/'.join((url.rstrip('/'), entry.name))

                if entry.smbc_type == self.DIRENT_TYPE_DIR:
                    dirstack.append(entry_url)
                    continue

                cifsfile = CifsFile(
                    self._context,
                    entry,
                    entry_url,
                    self.stat(entry_url)
                )

                cifsfile.read_allowed, cifsfile.read_denied = self.cifs_acls(entry_url)

                yield cifsfile

    def get_dir_entries(self, url):
        return (entry for entry in self._context.opendir(url).getdents() if entry.name not in ['.', '..'])

    def stat(self, url):
        # https://github.com/hamano/pysmbc/blob/master/smbc/context.c#L470
        fields = ('mode', 'ino', 'dev', 'nlink', 'uid', 'gid', 'size', 'atime', 'mtime', 'ctime')
        statdata = dict(zip(fields, self._context.stat(url)))
        return statdata

    def cifs_acls(self, url):
        perms = self._context.getxattr(url, "system.nt_sec_desc.*")

        acl = self.parse_cifsacl(perms)
        allowed = acl_sids(filter_acl_read(acl, ACE_ACCESS_ALLOWED))
        denied = acl_sids(filter_acl_read(acl, ACE_ACCESS_DENIED))

        return (allowed, denied)

    def parse_cifsacl(self, data):
        '''Parse Access Control List'''
        read_perms = []

        for line in data.split(","):
            user = parse_cifsace(line)
            if (user):
                read_perms.append(user)

        return read_perms

    def auth(self, ctx, server, workgroup, username, password):
        return (
            self._conf['domain'],
            self._conf['username'],
            self._conf['password']
        )


class CifsFile(File):

    _file = None

    _context = None

    def __init__(self, context, file, url, statdata):
        super().__init__()

        self._context = context
        self._file = file
        self.url = url

        self.created = datetime.datetime.fromtimestamp(statdata['ctime'])
        self.modified = datetime.datetime.fromtimestamp(statdata['mtime'])
        self.size = statdata['size']

    @contextmanager
    def open(self):
        try:
            f = self._context.open(self.url, os.O_RDONLY)
            yield f
        finally:
            f.close()
