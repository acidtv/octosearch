from setuptools import setup, find_packages

setup(
        name='duckysearch',
        packages=find_packages(),
        entry_points={
            'duckysearch.indexer': [
                'localfs = duckysearch.indexers.localfs.localfs:Localfs',
                'mountedcifs = duckysearch.indexers.mountedcifs.mountedcifs:Mountedcifs',
                ],
            'duckysearch.parser': [
                'application/pdf = duckysearch.parser.pdf:ParserPdf',
                'text/* = duckysearch.parser.text:ParserText',
                'application/octet-stream = duckysearch.parser.fallback:ParserFallback'
                ],
            'duckysearch.auth': [
                'ldap = duckysearch.auth.ldaphelper:LDAPAuth',
                ]
            }
        )
