from bs4 import BeautifulSoup


class ParserHtml:

    _metadata = {}

    def parse(self, file):
        content = ''

        with file.open() as f:
            soup = BeautifulSoup(f, 'lxml')

        # get_text() sometimes till returns bits of js, make sure those are gone before
        # calling get_text()
        for noindex in soup(['script', 'style']):
            noindex.decompose()

        content = soup.get_text()

        if soup.title:
            self._metadata['title'] = soup.title.string

        return content

    def extra(self):
        return self._metadata
