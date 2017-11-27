#!/usr/bin/python

import argparse

# from indexer import Indexer
# from elasticsearch import OutputElasticSearch
# from parserplugins import ParserPlugins

import duckysearch
from duckysearch import web, elasticsearch, parserplugins, indexer


class Ducky:
    def start(self, args):
        logger = Logger()
        backend = elasticsearch.OutputElasticSearch(args.es_server, args.index)
        parsers = parserplugins.ParserPlugins()

        main_indexer = indexer.Indexer(['conf-placeholder'])
        # indexer.ignore_extensions(self.ignore_extensions)

        # if args.check_removed:
            # indexer.check_removed()

        # if args.index_dir:
            # indexer.directory(args.index_dir)

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
    parser.add_argument('-cr', dest='check_removed', required=False, action='store_true', help='Check index for removed files.')
    parser.add_argument('--truncate', dest='truncate', required=False, action='store_true', help='Truncate index.')
    parser.add_argument('-i', dest='index_dir', required=False, help='Start indexing dir.')
    parser.add_argument('-if', dest='ignore_files', required=False, help='Files to ignore. Regular expressions can be used.')
    parser.add_argument('-im', dest='ignore_mimes', required=False, help='Mimetypes to ignore. Regular expressions can be used.')
    parser.add_argument('--es-server', dest='es_server', default='127.0.0.1', required=False, help='Elastic search server host.')
    parser.add_argument('--webserver', dest='webserver', required=False, action='store_true', help='Start the webserver interface.')
    parser.add_argument('index', help='The index to operate on')
    args = parser.parse_args()

    app = Ducky()
    app.start(args)
