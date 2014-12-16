Broad Crawl Limits
===

A Scrapy middleware to prevents too broad crawl when following large amount of internal/external links

Usage
---

In order to use it in your Scrapy project, please enable middleware in `settings.py`:

	SPIDER_MIDDLEWARES = {
   	   ...
   	   'broadcrawl.limits.BroadCrawlLimitsMiddleware': 100,
	}

Settings
---

You can change limit values by setting variables in `settings.py`:

   - `BCL_MAX_INTERNAL_LINKS` - max links from the same domain to follow on given page (default: 10)
   - `BCL_MAX_EXTERNAL_LINKS` - max links from external domain to follow on given page (default: 10)
   - `BCL_MAX_LINKS_PER_DOMAIN` - max total links per domain per crawl (default: 10)
   - `BCL_RANDOMIZE_LINKS` - randomize links to have better chance to get more relevant results (default: True)
   - `BCL_RANDOM_SEED` - seed for the link randomizer (default: 0)


Disable from spider
---
Please set `Request.meta['skip_broad_crawl_limits']` to True, and limits will be disabled for this request

Tests
---

Please type `tox` in command line to run unit-tests
