import re
import io


class ParserFallback:
    _pattern = '[a-z]'

    def types(self):
        return {'mimetypes': [None]}

    def find_words(self, content):
        # match all strings that look like words from 2 to 10 characters long
        return re.findall(self._pattern + '{3,20}', content, re.IGNORECASE)

    def parse(self, file):
        megabyte = 1024*1024

        # safety guard, so insanely big blobs won't get indexed
        if file.size > (megabyte*10):
            return ''

        content = '1'
        lastword = ''

        parsed = ''
        i = 0

        with io.TextIOWrapper(file.open(), encoding='utf-8', errors='replace') as f:
            while content:
                i = i + 1
                content = f.read(1024)

                if content.strip() == '':
                    continue

                if lastword:
                    sep = ' '

                    # test if first character is a word character
                    if re.match(self._pattern, content[0], re.IGNORECASE):
                        sep = ''

                    content = lastword + sep + content

                result = self.find_words(content)

                lastword = ''
                until = None

                # test if last character is a word character
                if result and re.match(self._pattern, content[-1], re.IGNORECASE) is not None:
                    lastword = result[-1]
                    until = -1

                parsed += self.compact(result[:until])

        print(parsed)
        return parsed

    def compact(self, regex_result):
        parsed = ''

        for word in regex_result:
            parsed += ' ' + word.lower()

        return parsed

    def extra(self):
        return {}
