from setuptools import setup, find_packages

setup(
        name='octosearch',
        packages=find_packages(),
        entry_points={
            'octosearch.indexer': [
                'localfs = octosearch.indexers.localfs.localfs:Localfs',
                'mountedcifs = octosearch.indexers.mountedcifs.mountedcifs:Mountedcifs',
                'http = octosearch.indexers.http.http:HttpCrawler',
                ],
            'octosearch.parser': [
                'application/pdf = octosearch.parser.pdf:ParserPdf',
                'text/plain = octosearch.parser.text:ParserText',
                'application/octet-stream = octosearch.parser.fallback:ParserFallback',
                'text/html = octosearch.parser.html:ParserHtml',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document = octosearch.parser.docx:ParserDocx'
                ],
            'octosearch.auth': [
                'ldap = octosearch.auth.ldaphelper:LDAPAuth',
                'basic = octosearch.auth.basic:BasicAuth',
                ]
            }
        )
