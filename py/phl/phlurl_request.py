"""Utilities for making requests with URLs."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlurl_request
#
# Public Classes:
#   Error
#
# Public Functions:
#   join_url
#   split_url
#   group_urls
#   get_many
#   get
#
# Public Assignments:
#   SplitUrlResult
#   GroupUrlResult
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================
from __future__ import absolute_import

import collections
import httplib
import traceback
import urlparse

_HTTPLIB_TIMEOUT = 600


def join_url(base_url, leaf):
    """Return the result of joining two parts of a url together.

    Usage Examples:

        >>> join_url('http://example.com/', 'mypage/')
        'http://example.com/mypage/'

        >>> join_url('http://example.com', 'mypage/')
        'http://example.com/mypage/'

    :base_url: the start of the new url
    :leaf: the end of the new url
    :returns: the joined url

    """
    return '/'.join([base_url.rstrip('/'), leaf])


SplitUrlResult = collections.namedtuple(
    'phlurl_request__SplitUrlResult',
    ['url', 'scheme', 'hostname', 'port', 'path'])

GroupUrlResult = collections.namedtuple(
    'phlurl_request__GroupUrlResult',
    ['http', 'https'])


class Error(Exception):
    pass


def split_url(url):
    """Returns a tuple (scheme, host, port, path) for using with httplib.

    You can use the 'scheme' part to choose between httplib.HTTPConnection or
    httplib.HTTPSConnection.

    You can use the 'host' and 'port' parts for the contruction of the
    connection.

    You can use the 'path' part in the request() call on the connection.

    Usage examples:
        >>> result = split_url('https://www.bloomberg.com:80/index')
        >>> result.scheme, result.hostname, result.port, result.path
        ('https', 'www.bloomberg.com', 80, '/index')

        >>> result = split_url('HTTPS://WWW.BLOOMBERG.COM:80/INDEX')
        >>> result.scheme, result.hostname, result.port, result.path
        ('https', 'www.bloomberg.com', 80, '/INDEX')

        >>> result = split_url('https://www.bloomberg.com/index')
        >>> result.scheme, result.hostname, result.port, result.path
        ('https', 'www.bloomberg.com', None, '/index')

        >>> result = split_url('https://www.bloomberg.com/index?a=index&b=c')
        >>> result.scheme, result.hostname, result.port, result.path
        ('https', 'www.bloomberg.com', None, '/index?a=index&b=c')

    :url: a fully qualified url
    :returns: a SplitUrlResult

    """
    original_url = url
    url = urlparse.urlsplit(url)

    # pylint: disable=E1103
    # pylint doesn't seem to know the members of SplitResult
    if url.query:
        path = '?'.join([url.path, url.query])
    else:
        path = url.path

    return SplitUrlResult(
        original_url, url.scheme, url.hostname, url.port, path)
    # pylint: enable=E1103


def group_urls(url_list):
    """Return a GroupUrlResult(http_requests, https_requests) from 'url_list'.

    Each of the dicts is layed out like:
        { (hostname, port): [path1, path2] }

    This is so that is then trivial to re-use http connections for requests
    to the same host.

    e.g.  { ('www.bloomberg.com', 80): '/index?a=index&b=c' }

    Usage examples:
        >>> result = group_urls(['http://a.io/a', 'http://a.io/b'])
        >>> dict(result.http)
        {('a.io', None): [('/a', 'http://a.io/a'), ('/b', 'http://a.io/b')]}
        >>> dict(result.https)
        {}

    :url_list: a list of string fully qualified urls
    :returns: a tuple of dicts which map connection params to paths

    """
    http_requests = collections.defaultdict(list)
    https_requests = collections.defaultdict(list)
    for url in url_list:
        request = split_url(url)
        if request.scheme == 'http':
            d = http_requests
        elif request.scheme == 'https':
            d = https_requests
        else:
            raise Error(str(url) + ' is neither http or https')
        connection = (request.hostname, request.port)
        result = (request.path, request.url)
        d[connection].append(result)
    return GroupUrlResult(http=http_requests, https=https_requests)


def _request(connection, verb, path, url):
    try:
        connection.request(verb, path)
        content = connection.getresponse().read()
        return content
    except Exception as e:
        tb = traceback.format_exc()
        message = """Was trying to {verb} the url {url}.

This exception was triggered from this original exception:
    {exception}

Here is the original traceback:
{traceback}
        """.format(verb=verb, url=url, exception=repr(e), traceback=tb).strip()
        raise Error(message)


def get_many(url_list):
    """Return a dict of {url: content_str} from the supplied 'url_list'.

    Attempts to re-use connections where possible.

    Note that this shouldn't be used to download large files, there is a
    default timeout in place to prevent blocking for large amounts of time.

    :url_list: a list of string urls, e.g. 'http://www.bloomberg.com/'
    :returns: a list of string contents

    """
    urls = group_urls(url_list)
    results = {}

    for host_port, request_list in urls.http.iteritems():
        http = httplib.HTTPConnection(
            host_port[0], host_port[1], timeout=_HTTPLIB_TIMEOUT)
        for path, url in request_list:
            results[url] = _request(http, 'GET', path, url)

    for host_port, request_list in urls.https.iteritems():
        https = httplib.HTTPSConnection(
            host_port[0], host_port[1], timeout=_HTTPLIB_TIMEOUT)
        for path, url in request_list:
            results[url] = _request(https, 'GET', path, url)

    return results


def get(url):
    """Return the content of the supplied url.

    Note that this shouldn't be used to download large files, there is a
    default timeout in place to prevent blocking for large amounts of time.

    :url: a string url, e.g. 'http://www.bloomberg.com/'
    :returns: the string content

    """
    return get_many([url])[url]


#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------
