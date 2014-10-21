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
from __future__ import division
from __future__ import print_function

import base64
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
    ['url', 'scheme', 'hostname', 'port', 'path', 'username', 'password'])

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
        original_url,
        url.scheme,
        url.hostname,
        url.port,
        path,
        url.username,
        url.password)
    # pylint: enable=E1103


def _group_urls(url_list):
    """Return a GroupUrlResult(http_requests, https_requests) from 'url_list'.

    Each of the dicts is layed out like:
        { (hostname, port): [path1, path2] }

    This is so that is then trivial to re-use http connections for requests
    to the same host.

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
        d[connection].append(request)
    return GroupUrlResult(http=http_requests, https=https_requests)


def _request(connection, verb, request):
    try:
        headers = {}
        if request.username:
            auth = base64.b64encode(
                '%s:%s' % (request.username, request.password))
            headers['Authorization'] = 'Basic %s' % auth
        connection.request(method=verb,
                           url=request.path,
                           headers=headers)
        response = connection.getresponse()
        return (response.status, response.read())
    except Exception as e:
        tb = traceback.format_exc()
        message = """Was trying to {verb} the url {request.url}.

This exception was triggered from this original exception:
    {exception}

Here is the original traceback:
{traceback}
        """.format(
            verb=verb,
            request=request,
            exception=repr(e),
            traceback=tb
        ).strip()

        raise Error(message)


def get_many(url_list):
    """Return a dict of {url: content_str} from the supplied 'url_list'.

    Attempts to re-use connections where possible.

    Note that this shouldn't be used to download large files, there is a
    default timeout in place to prevent blocking for large amounts of time.

    :url_list: a list of string urls, e.g. 'http://www.bloomberg.com/'
    :returns: a list of string contents

    """
    urls = _group_urls(url_list)
    results = {}

    for host_port, request_list in urls.http.iteritems():
        http = httplib.HTTPConnection(
            host_port[0], host_port[1], timeout=_HTTPLIB_TIMEOUT)
        for request in request_list:
            results[request.url] = _request(http, 'GET', request)

    for host_port, request_list in urls.https.iteritems():
        https = httplib.HTTPSConnection(
            host_port[0], host_port[1], timeout=_HTTPLIB_TIMEOUT)
        for request in request_list:
            results[request.url] = _request(https, 'GET', request)

    return results


def get(url):
    """Return the content of the supplied url.

    Note that this shouldn't be used to download large files, there is a
    default timeout in place to prevent blocking for large amounts of time.

    :url: a string url, e.g. 'http://www.bloomberg.com/'
    :returns: the string content

    """
    return get_many([url])[url]


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2015 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
