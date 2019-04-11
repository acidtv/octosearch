import requests
import logging


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

        if response.status_code == 415:
            logging.error('Tika does not support the media type of file {} (Got HTTP 415)'.format(file.url))
            return ''

        if response.status_code == 422:
            logging.error('Tika cannot process this file {}. This can happen if the mime-type is unsupported, the document is encrypted, etc. (Got HTTP 422)'.format(file.url))
            return ''

        if not response.ok:
            raise Exception('Could not parse {} with Tika, response code: {}, response: {}'.format(file.url, response.status_code, response.text))

        data = response.json()
        content = ''

        try:
            data = data[0]
        except Exception:
            raise Exception('Could not parse ' + file.url)

        if 'X-TIKA:content' in data:
            content = data['X-TIKA:content']
            del data['X-TIKA:content']

        # Temporarily disable indexing all metadata, because we easily
        # bump into ES's index.mapping.total_fields.limit
        # self._extra = data

        return content

    def extra(self):
        '''Return extra info'''

        return self._extra
