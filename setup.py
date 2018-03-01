from setuptools import setup, find_packages

setup(
        name='octosearch',
        packages=find_packages(),
        entry_points={
            'octosearch.indexer': [
                'localfs = octosearch.indexers.localfs.localfs:Localfs',
                'mountedcifs = octosearch.indexers.mountedcifs.mountedcifs:Mountedcifs',
                ],
            'octosearch.parser': [
                'application/pdf = octosearch.parser.pdf:ParserPdf',
                'text/* = octosearch.parser.text:ParserText',
                'application/octet-stream = octosearch.parser.fallback:ParserFallback'
                ],
            'octosearch.auth': [
                'ldap = octosearch.auth.ldaphelper:LDAPAuth',
                ]
            }
        )
