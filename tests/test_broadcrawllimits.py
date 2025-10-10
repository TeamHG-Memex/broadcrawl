import unittest
from collections import defaultdict

import scrapy
from scrapy.settings import Settings

from broadcrawl.limits import BroadCrawlLimitsMiddleware


class BroadCrawlLimitsTestCase(unittest.TestCase):

    def setUp(self):
        self.last_ids = defaultdict(int)

    def test_max_internal_links_is_obeyed(self):
        domain = 'domain1.com'
        requests = self._generate_requests({
            'domain1.com': 100,
        })
        middleware = self._create_middleware(max_internal_links=10)
        filtered = self._run_middleware(middleware, domain, requests)
        self.assertEqual(len(filtered), 10)

    def test_max_external_links_is_obeyed(self):
        domain = 'domain1.com'
        requests = self._generate_requests({
            'domain2.com': 50,
            'domain3.com': 50,
        })
        middleware = self._create_middleware(max_external_links=10)
        filtered = self._run_middleware(middleware, domain, requests)
        self.assertEqual(len(filtered), 10)

    def test_external_links_per_domain_is_obeyed(self):
        domain = 'domain1.com'
        requests = self._generate_requests({
            'domain2.com': 50,
            'domain3.com': 50,
        })
        middleware = self._create_middleware(max_links_per_domain=10)
        filtered = self._run_middleware(middleware, domain, requests)
        self.assertEqual(len(filtered), 20)

        # There should be 10 requests to domain1 and 10 to domain2
        counts = [0, 0]
        for r in filtered:
            if 'domain2.com' in r.url:
                counts[0] += 1
            elif 'domain3.com' in r.url:
                counts[1] += 1
        self.assertEqual(counts[0], 10)
        self.assertEqual(counts[1], 10)

        # Run again, there should be no more requests to those domains, since
        # limit was reached
        filtered = self._run_middleware(middleware, domain, requests)
        self.assertEqual(len(filtered), 0)

    def test_randomize_links(self):
        requests = self._generate_requests({
            'domain1.com': 100,
        })
        middleware = self._create_middleware(randomize_links=True)
        filtered = self._run_middleware(middleware, 'domain1.com', requests)
        assert(filtered[0].url.endswith('/24'))

    def _run_middleware(self, middleware, domain, requests):
        request = scrapy.Request(url='http://%s' % domain)
        response = scrapy.http.Response(request.url, request=request)
        filtered = middleware.process_spider_output(response, requests, None)
        return list(filtered)

    def _create_middleware(self, max_internal_links=1000,
                           max_external_links=1000,
                           max_links_per_domain=1000,
                           randomize_links=False,
                           random_seed=0):
        settings = Settings({
            'BCL_MAX_INTERNAL_LINKS': max_internal_links,
            'BCL_MAX_EXTERNAL_LINKS': max_external_links,
            'BCL_MAX_LINKS_PER_DOMAIN': max_links_per_domain,
            'BCL_RANDOMIZE_LINKS': randomize_links,
            'BCL_RANDOM_SEED': random_seed,
        })
        return BroadCrawlLimitsMiddleware(settings)

    def _generate_requests(self, domain_counts):
        for domain, count in domain_counts.items():
            for i in range(count):
                yield self._get_next_request(domain)

    def _get_next_request(self, domain):
        self.last_ids[domain] += 1
        url = 'http://%s/%d' % (domain, self.last_ids[domain])
        return scrapy.Request(url)
