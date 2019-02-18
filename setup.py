from setuptools import setup, find_packages

setup(
        name='octosearch',
        packages=find_packages(),
        entry_points={
            'octosearch.indexer': [
                'localfs = octosearch.indexers.localfs.localfs:Localfs',
                'mountedcifs = octosearch.indexers.mountedcifs.mountedcifs:Mountedcifs',
                'http = octosearch.indexers.http.http:HttpCrawler',
                'pyfilesystem = octosearch.indexers.pyfilesystem.pyfilesystem:Pyfilesystem',
                'cifs = octosearch.indexers.cifs.cifs:Cifs',
                ],
            'octosearch.parser': [
                'pdf = octosearch.parser.pdf:ParserPdf',
                'text = octosearch.parser.text:ParserText',
                'fallback = octosearch.parser.fallback:ParserFallback',
                'html = octosearch.parser.html:ParserHtml',
                'docx = octosearch.parser.docx:ParserDocx',
                'tika = octosearch.parser.tika:ParserTika',
                ],
            'octosearch.auth': [
                'ldap = octosearch.auth.ldaphelper:LDAPAuth',
                'basic = octosearch.auth.basic:BasicAuth',
                ]
            }
        )
