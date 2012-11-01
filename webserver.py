import BaseHTTPServer
import re
import os
import json
from urlparse import urlparse

def start(backend):
	address = ('', 8080)
	server = DuckyWebServer(address, DuckyWebRequest)
	server.set_backend(backend)
	server.serve_forever()

class DuckyWebServer(BaseHTTPServer.HTTPServer):
	backend = None

	def set_backend(self, backend):
		self.backend = backend

class DuckyWebRequest(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		self._handle_request('get')

	def do_POST(self):
		self._handle_request('post')

	def _handle_request(self, method):
		'''Handle POST and GET requests'''
		path = self.path.split('/')

		if path[1] == 'api':
			self.handle_api_request(method, path[2:]);
			return

		self.serve_file(path[1])

	def serve_file(self, filename = ''):
		if filename == '':
			filename = 'index.htm'

		# check for valid filename
		if not re.match('[a-z_\.\-0-9]+', filename):
			self.send_error(403)
			return

		filepath = os.path.dirname(__file__) + '/web/' + filename

		# serve file
		try:
			f = open(filepath, 'r')
		except IOError:
			self.send_error(404)
			return

		self.send_response(200)
		self.end_headers()

		while True:
			chunk = f.read(1024)

			if not chunk:
				break

			self.wfile.write(chunk)

		f.close()

	def handle_api_request(self, method, path):
		'''Proxies api requests to the backend'''

		if path[0] != 'elasticsearch':
			self.send_error(404)
			return

		joined_path = '/'.join(path[1:])
		url = urlparse(path[2])

		if url.path != '_search':
			self.send_error(403)
			return

		es_path = '/' + joined_path
		print 'es path', joined_path

		data = self.server.backend._es_call(method, joined_path)

		self.send_response(200)
		self.end_headers()

		response = json.dumps(data)
		self.wfile.write(response)

		return
