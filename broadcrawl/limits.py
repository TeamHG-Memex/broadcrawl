import random
from collections import defaultdict

import scrapy

from broadcrawl.utils import is_external_url, get_domain
from broadcrawl.utils import split_list


class BroadCrawlLimitsMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.max_internal_links = settings.getint('BCL_MAX_INTERNAL_LINKS', 10)
        self.max_external_links = settings.getint('BCL_MAX_EXTERNAL_LINKS', 10)
        self.max_links_per_domain = settings.getint('BCL_MAX_LINKS_PER_DOMAIN',
                                                    10)
        self.randomize_links = settings.getbool('BCL_RANDOMIZE_LINKS', False)
        self.random_seed = settings.getbool('BCL_RANDOM_SEED', 0)
        self.random = random.Random(self.random_seed)
        self.links_per_domain_counts = defaultdict(int)

    def process_spider_output(self, response, result, spider):
        if response.meta.get('skip_broad_crawl_limits'):
            return result
        requests, items = split_list(result,
                                     lambda r: isinstance(r, scrapy.Request))
        if self.randomize_links:
            requests = self._randomize_requests(requests)

        requests = self._filter_internal_links_count(requests, response)
        requests = self._filter_external_links_count(requests, response)
        requests = self._filter_domain_limit(requests)

        return list(requests) + list(items)

    def _randomize_requests(self, requests):
        requests = list(requests)
        self.random.shuffle(requests)
        return requests

    def _filter_domain_limit(self, requests):
        for r in requests:
            domain = get_domain(r.url)
            doesnt_exceeds_domain_limit = (
                self.links_per_domain_counts[domain] <
                self.max_links_per_domain
            )
            if doesnt_exceeds_domain_limit:
                self.links_per_domain_counts[domain] += 1
                yield r

    def _filter_internal_links_count(self, requests, response):
        internal_links_count = 0
        print(requests)
        for r in requests:
            max_internal_links = r.meta.get('max_internal_links',
                                            self.max_internal_links)
            if not is_external_url(response.url, r.url):
                if internal_links_count < max_internal_links:
                    yield r
                internal_links_count += 1
            else:
                yield r

    def _filter_external_links_count(self, requests, response):
        external_links_count = 0
        for r in requests:
            max_external_links = r.meta.get('max_external_links',
                                            self.max_external_links)
            if is_external_url(response.url, r.url):
                if external_links_count < max_external_links:
                    yield r
                external_links_count += 1
            else:
                yield r
