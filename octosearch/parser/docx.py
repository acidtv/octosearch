from docx import Document


class ParserDocx(object):

    def __init__(self, conf):
        pass

    def types(self):
        return ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']

    def parse(self, file):

        content = ''

        with file.open() as f:
            doc = Document(f)

            for paragraph in doc.paragraphs:
                content = content + ' ' + paragraph.text

        return content

    def extra(self):
        return {}
