#!/usr/bin/python

import argparse

from duckysearch import web, parserplugins, config
from duckysearch.indexers import mountedcifs
from duckysearch.backends import elasticsearch


class Ducky:
    def start(self, args):
        logger = Logger()
        parsers = parserplugins.ParserPlugins()
        conf = config.Config()

        # main_indexer = indexer.Indexer(['conf-placeholder'])
        # indexer.ignore_extensions(self.ignore_extensions)

        # if args.check_removed:
        #     indexer.check_removed()

        if args.index_dir:
            elastic_backend = elasticsearch.BackendElasticSearch(conf.get('backend', 'server'), conf.get('backend', 'index'))
            cifs_indexer = mountedcifs.Mountedcifs(logger, elastic_backend, parsers)
            cifs_indexer.directory(args.index_dir)

        # if args.truncate:
            # backend.truncate()

        if args.webserver:
            web.app.run(debug=True)

    def ignore_extensions(self):
        return ['swp', 'bin', 'rar', 'iso', 'img', 'zip']


class Logger:
    def add(self, text):
        print text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filesystem indexer')
    parser.add_argument('-i', dest='index_dir', required=False, help='Start indexing dir.')
    parser.add_argument('--webserver', dest='webserver', required=False, action='store_true', help='Start the webserver interface.')
    parser.add_argument('-cr', dest='check_removed', required=False, action='store_true', help='Check index for removed files.')
    parser.add_argument('--truncate', dest='truncate', required=False, action='store_true', help='Truncate index.')
    parser.add_argument('-if', dest='ignore_files', required=False, help='Files to ignore. Regular expressions can be used.')
    parser.add_argument('-im', dest='ignore_mimes', required=False, help='Mimetypes to ignore. Regular expressions can be used.')
    args = parser.parse_args()

    app = Ducky()
    app.start(args)
