import pdftotext


class ParserPdf:
    _extra = {}

    def types(self):
        return {
                'mimetypes': ['application/pdf']
                }

    def parse(self, file):
        with file.open() as f:
            pdf = pdftotext.PDF(f)
            pages = len(pdf)
            text = "\n\n".join(pdf)

        self._extra['pages'] = pages

        return text

    def extra(self):
        '''Return extra info'''

        return self._extra
