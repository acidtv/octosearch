import hashlib


class BasicAuth(object):

    _conf = {}

    def __init__(self, conf):
        self._conf = conf

    def authenticate(self, username, password):
        if username.strip() == '' or password.strip() == '':
            return False

        pwd_hash = hashlib.md5(password.encode()).hexdigest()

        print(pwd_hash)
        if username == self._conf['username'] and pwd_hash == self._conf['password_hash']:
            return True

        return False

    def groups(self):
        return []
