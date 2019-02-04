import pdftotext


class ParserPdf(object):
    _extra = {}

    def __init__(self, conf):
        pass

    def types(self):
        return ['application/pdf']

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
