import BaseHTTPServer
import re
import os
import json
from urlparse import urlparse

from . import app
from flask import render_template, request
from .. import ldaphelper


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        ldap = ldaphelper.LDAPHelper()
        ldap.connect()
        ldap.authenticate(request.form['username'], request.form['password'])

    return render_template('login.html')

class DuckyWebRequest(BaseHTTPServer.BaseHTTPRequestHandler):
	"""Obsolete webserver class. Keeping it around for api request forwarder code"""

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
