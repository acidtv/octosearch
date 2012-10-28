
from pyPdf.pdf import PdfFileReader

class ParserPdf:
	_extra = {}

	def types(self):
		return {
			'mimetypes': ['application/pdf']
		}

	def parse(self, file_full, statdata):
		pdf = PdfFileReader(file(file_full, 'rb'))

		pages = pdf.getNumPages()
		text = ''

		self._extra['pages'] = pages

		for pagenr in range(pages):
			page = pdf.getPage(pagenr-1)
			text += ' ' + page.extractText()

		return text

	def extra(self):
		'''Return extra info'''

		return self._extra