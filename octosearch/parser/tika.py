import requests


class ParserTika(object):
    _extra = {}

    _conf = {}

    def __init__(self, conf):
        self._conf = conf

    def types(self):
        headers = {'accept': 'application/json'}
        response = requests.get(self._conf['url'] + '/mime-types', headers=headers)
        data = response.json()

        return data.keys()

    def parse(self, file):
        headers = {'accept': 'application/json'}

        with file.open() as f:
            response = requests.put(self._conf['url'] + '/rmeta/text', data=f, headers=headers)

        data = response.json()
        content = ''

        try:
            data = data[0]
        except Exception:
            raise Exception('Could not parse ' + file.url)

        if 'X-TIKA:content' in data:
            content = data['X-TIKA:content']

        del data['X-TIKA:content']

        self._extra = data

        return content

    def extra(self):
        '''Return extra info'''

        return self._extra
