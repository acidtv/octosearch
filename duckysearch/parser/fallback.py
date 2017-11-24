import re

class ParserFallback:
	def types(self):
		return {'mimetypes': [None]}

	def parse(self, file, statdata):
		megabyte = 1024*1024

		# safety guard, so insanely big blobs won't get indexed
		if statdata.st_size > (megabyte*10):
			return ''

		f = open(file)
		
		content = '1'
		lastword = ''

		pattern = '[a-z]'

		parsed = ''
		i = 0

		while content:
			i = i + 1
			content = f.read(1024)

			if content.strip() == '':
				continue

			# test if first character is a word character
			if lastword and re.match(pattern, content[0], re.IGNORECASE):
				content = lastword + content

			# match all strings that look like words from 2 to 10 characters long
			result = re.findall(pattern + '{2,10}', content, re.IGNORECASE)

			lastword = ''
			until = None
			# test if last character is a word character
			if result and re.match(pattern, content[-1], re.IGNORECASE) != None:
				lastword = result[-1]
				until = -1

			for word in result[:until]:
				parsed += ' ' + word.lower()

		return parsed

	def extra(self):
		return {}
				