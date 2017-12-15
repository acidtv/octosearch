
class Dummybackend(object):

    def add(self, id, info):
        """Add new document to index"""
        return

    def get_all(self):
        return []

    def get_keys(self, keys):
        '''Returns list with specified keys'''
        return []

    def remove(self, files):
        '''Remove files from index'''
        return

    def truncate(self):
        '''Empty the entire index'''
        return
