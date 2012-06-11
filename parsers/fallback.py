import re

class Parser_Fallback:
	def mime_types(self):
		return [None]

	def parse(self, file):
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

			result = re.findall(pattern + '{2,}', content, re.IGNORECASE)

			lastword = ''
			until = None
			# test if last character is a word character
			if result and re.match(pattern, content[-1], re.IGNORECASE) != None:
				lastword = result[-1]
				until = -1

			for word in result[:until]:
				parsed += ' ' + word.lower()

		return parsed
				