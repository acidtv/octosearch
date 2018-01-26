import PyPDF2


class ParserPdf:
    _extra = {}

    def types(self):
        return {
                'mimetypes': ['application/pdf']
                }

    def parse(self, file):
        with file.open_binary() as f:
            pdf = PyPDF2.PdfFileReader(f)

            pages = pdf.getNumPages()
            text = ''

            self._extra['pages'] = pages

            for pagenr in range(pages):
                page = pdf.getPage(pagenr)
                text += ' ' + page.extractText()

        return text

    def extra(self):
        '''Return extra info'''

        return self._extra
