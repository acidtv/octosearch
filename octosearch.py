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

            if args.truncate:
                elastic_backend.truncate()

            if args.index is not None:
                index_job = indexer.Indexer(logger=log, backend=elastic_backend, parsers=parserplugins.ParserPlugins(conf.get('parser')))
                indexes = None

                if args.index is True:
                    indexes = conf.get('indexer')
                else:
                    for indexer_conf in conf.get('indexer'):
                        if indexer_conf['name'] == args.index:
                            indexes = [indexer_conf]

                    if indexes is None:
                        raise Exception('Index not found: %s' % args.index)

                for indexer_conf in indexes:
                    log.add('Indexing ' + indexer_conf['name'])
                    index_job.index(indexer_conf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filesystem indexer')
    parser.add_argument(
        '--index',
        dest='index',
        required=False,
        action='store',
        nargs='?',
        const=True,
        help='Start indexing.'
    )
    parser.add_argument('--webserver', dest='webserver', required=False, action='store_true', help='Start the webserver interface.')
    parser.add_argument('--truncate', dest='truncate', required=False, action='store_true', help='Truncate index.')
    parser.add_argument(
        '--config',
        dest='config',
        required=False,
        help='Specify a config file. Defaults to config.ini in current folder.',
        default='config.ini')
    args = parser.parse_args()

    app = Octo()
    app.start(args)
