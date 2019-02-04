import requests


class ParserTika(object):
    _extra = {}

    _conf = {}

    def __init__(self, conf):
        self._conf = conf

    def types(self):
        # FIXME do request to tikaserver to get supported mimes
        return []

    def parse(self, file):
        headers = {'accept': 'application/json'}

        with file.open() as f:
            response = requests.put(self._conf['url'] + '/rmeta/text', data=f, headers=headers)

        data = response.json()

        if 'X-TIKA:content' in data[0]:
            return data[0]['X-TIKA:content']

        return ''

    def extra(self):
        '''Return extra info'''

        return self._extra
