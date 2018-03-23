from docx import Document


class ParserDocx:

    def parse(self, file):

        content = ''

        with file.open_binary() as f:
            doc = Document(f)

            for paragraph in doc.paragraphs:
                content = content + ' ' + paragraph.text

        return content

    def extra(self):
        return {}
