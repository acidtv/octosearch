import httplib
import json
import math

class Output_ElasticSearch:

	server = None

	index = None

	def __init__(self, server, index):
		self.server = server
		self.index = index

	def add(self, id, info):
		"""Add new document to index"""

		self._es_call('put', '/' + self.index + '/document/' + id, info)

	def get_all(self):
		'''Generator. Returns the entire index'''

		result = self._es_call('get', '/' + self.index + '/document/_search?path:*', None)

		pagesize = 100
		pages = int(math.ceil(result['hits']['total']/(pagesize+.0)))

		for page in range(pages):
			pagefrom = (pagesize*page)
			url = '/' + self.index + '/document/_search?path:*&fields=path,filename&from=' + str(pagefrom) + '&size=' + str(pagesize)
			result = self._es_call('get', url, None)

			for document in result['hits']['hits']:
				try:
					dump = {'path': document['fields']['path'], 'filename': document['fields']['filename']}
				except KeyError:
					continue

				yield dump

	def _es_call(self, method, url, content):
		'''Call elastic search server'''

		jsondoc = ''

		if content:
			jsondoc = json.dumps(content)

		httpcon = httplib.HTTPConnection(self.server, 9200)
		httpcon.request(method.upper(), url, jsondoc)
		response = httpcon.getresponse()

		jsondoc = json.loads(response.read())

		httpcon.close()

		return jsondoc

