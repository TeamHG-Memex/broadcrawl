# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import urlparse


def split_list(list_, condition):
    """Split list into two lists based on condition"""
    true, false = [], []
    for item in list_:
        if condition(item):
            true.append(item)
        else:
            false.append(item)
    return true, false


has_scheme = re.compile(r"[a-z]+://.+", re.IGNORECASE).match


def get_domain(url):
    host = urlparse.urlparse(url).netloc
    if ":" in host:
        host.split(":", 1)[0]
    return host


def get_hostname(url):
    """
    Return the hostname ``url`` belongs to; 'www' is stripped.

    >>> get_hostname("http://example.com/sdf")
    'example.com'
    >>> get_hostname("http://www.example.com/")
    'example.com'
    >>> get_hostname("http://www2.example.com/")
    'example.com'
    >>> get_hostname("http://www.static.example.com/")
    'static.example.com'
    >>> get_hostname("http://awww.static.example.com/")
    'awww.static.example.com'
    >>> get_hostname("http://static.example.com/")
    'static.example.com'
    >>> get_hostname("fsdf")
    'fsdf'
    >>> get_hostname("127.0.0.1")
    '127.0.0.1'
    """
    url = add_scheme_if_missing(url)
    try:
        domain = urlparse.urlparse(url).hostname or ''
    except Exception:
        domain = ''
    else:
        domain = re.sub(r'^www\d*\.', '', domain)
    return domain


def add_scheme_if_missing(url):
    """
    Add scheme to an url if it is missing.

    >>> add_scheme_if_missing("example.com")
    'http://example.com'
    >>> add_scheme_if_missing("https://example.com")
    'https://example.com'
    >>> add_scheme_if_missing("ftp://example.com")
    'ftp://example.com'
    """
    url = url.strip()
    return url if has_scheme(url) else "http://" + url


def get_robotstxt_url(url):
    """
    >>> get_robotstxt_url("https://example.com/foo/bar?baz=1")
    'https://example.com/robots.txt'
    """
    if not isinstance(url, urlparse.ParseResult):
        url = urlparse.urlparse(url)
    return "%s://%s/robots.txt" % (url.scheme, url.netloc)


def is_external_url(source_url, target_url):
    """
    Return True if URLs are external to each other.

    >>> is_external_url("http://example.com/foo", "http://example.com/bar")
    False
    >>> is_external_url("http://example.com/foo", "http://example2.com/bar")
    True

    Subdomains are not considered external:

    >>> is_external_url("http://example.com", "http://static.example.com")
    False

    If the domain is the same but TLDs differ links are also *not* considered
    external:

    >>> is_external_url("http://example.com", "http://static.example.co.uk")
    False
    """
    p1 = get_hostname(source_url)
    p2 = get_hostname(target_url)
    return p1 != p2

if __name__ == "__main__":
    print get_domain("http://3223423wfawefawf.onion")
