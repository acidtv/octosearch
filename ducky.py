#!/usr/bin/python

from indexer import Indexer
from elasticsearch import Output_ElasticSearch

class Ducky:
	def start(self):
		logger = Logger()
		output = Output_ElasticSearch('127.0.0.1', 'ducky')
		indexer = Indexer(logger, output)
		
		indexer.check_removed()
		
		#indexer.directory('/home/alex/code/ducky')


class Logger:
	def add(self, text):
		print '[LOG]:', text

app = Ducky()
app.start()