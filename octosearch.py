#!/usr/bin/env python

import argparse

from octosearch import web, config, indexer, parserplugins, logger
from octosearch.backends import elasticsearch


class Octo:
    def start(self, args):
        conf = config.Config(args.config)
        log = logger.Logger()

        if args.webserver:
            web.app.run(debug=True)
        else:
            elastic_backend = elasticsearch.BackendElasticSearch(conf.get('backend', 'server'), conf.get('backend', 'index'))

            # FIXME
            # if args.check_removed:
            #     indexer.check_removed()

            if args.truncate:
                elastic_backend.truncate()

            if args.index:
                index_job = indexer.Indexer()
                index_job.logger = log
                index_job.backend = elastic_backend
                index_job.parsers = parserplugins.ParserPlugins()

                for indexer_conf in conf.get('indexer'):
                    log.add('Indexing ' + indexer_conf['name'])
                    index_job.index(indexer_conf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filesystem indexer')
    parser.add_argument('--index', dest='index', required=False, action='store_true', help='Start indexing.')
    parser.add_argument('--webserver', dest='webserver', required=False, action='store_true', help='Start the webserver interface.')
    parser.add_argument('--truncate', dest='truncate', required=False, action='store_true', help='Truncate index.')
    parser.add_argument(
        '--config',
        dest='config',
        required=False,
        help='Specify a config file. Defaults to config.ini in current folder.',
        default='config.ini')
    # parser.add_argument('-cr', dest='check_removed', required=False, action='store_true', help='Check index for removed files.')
    # parser.add_argument('-if', dest='ignore_files', required=False, help='Files to ignore. Regular expressions can be used.')
    # parser.add_argument('-im', dest='ignore_mimes', required=False, help='Mimetypes to ignore. Regular expressions can be used.')
    args = parser.parse_args()

    app = Octo()
    app.start(args)
