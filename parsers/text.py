
class ParserText:
	def types(self):
		return {
			'expressions': ['text/*']
		}

	def parse(self, file_full, statdata):
		'''Dump file contents straight back to indexer'''

		file = open(file_full, 'r')

		content = file.read()
		file.close

		return content

	def extra(self):
		return {}
