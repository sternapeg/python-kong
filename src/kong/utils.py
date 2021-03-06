# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import time
import uuid
from json import dumps

import six

from .compat import urlparse, urlencode, unquote, parse_qs, parse_qsl, ParseResult, OrderedDict, utf8_or_str


def timestamp():
    """
    Returns a unix timestamp
    :return:
    """
    return int(time.time())


def sorted_ordered_dict(d, key=None):
    key = key or (lambda t: t[0])
    return OrderedDict(sorted(d.items(), key=key))


def uuid_or_string(data):
    """
    Convenience method
    :param data:
    :return:
    """
    if isinstance(data, uuid.UUID):
        return str(data)
    elif isinstance(data, six.string_types):
        return data
    raise ValueError('Expected string or UUID, got %r' % data)


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'

    Source: http://stackoverflow.com/a/25580545/591217
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(utf8_or_str(url))  # ``unquote`` operates on BYTES, not unicode strings...

    # Extracting url info
    parsed_url = urlparse(url)

    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query

    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))

    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    # Bool and Dict values should be converted to json-friendly values
    json_friendly_data = {}
    for k, v in parsed_get_args.items():
        if isinstance(v, (bool, dict)):
            json_friendly_data[k] = dumps(v)
    parsed_get_args.update(json_friendly_data)

    parsed_get_args = sorted_ordered_dict(parsed_get_args)

    # Encoding parsed args to given encoding to make sure ``urlencode`` does not try to "encode" the string himself
    # because he is clearly not able to do it correctly. (See the comments inside the function for the ins and outs)
    parsed_get_args_encoded = OrderedDict(
        (k, utf8_or_str(v) if isinstance(v, six.text_type) else v)
        for k, v in parsed_get_args.items()
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args_encoded, doseq=True)

    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url


def assert_dict_keys_in(d, allowed_keys, error_template=None):
    error_template = error_template or '%r is not a valid key. Allowed keys: %r'
    for key in d:
        assert key in allowed_keys, error_template % (key, allowed_keys)


def ensure_trailing_slash(url):
    if not url.endswith('/'):
        url = '%s/' % url
    return url


def parse_query_parameters(url):
    return parse_qs(urlparse(url).query)
