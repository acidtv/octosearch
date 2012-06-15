
from pyPdf.pdf import PdfFileReader

class ParserPdf:
	def types(self):
		return {
			'mimetypes': ['application/pdf']
		}

	def parse(self, file_full, statdata):
		pdf = PdfFileReader(file(file_full, 'rb'))

		pages = pdf.getNumPages()
		text = ''

		for pagenr in range(pages):
			page = pdf.getPage(pagenr-1)
			text += ' ' + page.extractText()

		return text