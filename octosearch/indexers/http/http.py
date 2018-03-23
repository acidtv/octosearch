import requests
import re
from queue import LifoQueue
from ...indexer import MemoryFile
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class HttpCrawler(object):

    def index(self, conf):

        session = requests.session()
        urls = LifoQueue()

        allowed_domains = conf['allowed_domains'].split(',')
        start = conf['url']
        ignore = re.compile(conf['ignore'])

        found = set([start])
        urls.put(start)

        while not urls.empty():
            url = urls.get()

            r = session.get(url)

            for link in BeautifulSoup(r.content).find_all('a'):
                link_href = link.get('href')

                if not link_href:
                    continue

                if link_href.startswith('/'):
                    link_href = urljoin(url, link_href)

                parsed = urlparse(link_href)

                if parsed.hostname not in allowed_domains:
                    continue

                if ignore.match(link_href):
                    continue

                if link_href not in found:
                    found.add(link_href)
                    urls.put(link_href)

            metadata = {
                'url': url,
                # FIXME
                'mimetype': 'text/html',
                'extension': 'html',
                'size': 0,
                'modified': None,
            }

            yield MemoryFile(r.content, metadata)
