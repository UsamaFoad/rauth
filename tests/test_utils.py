# -*- coding: utf-8 -*-
'''
    rauth.test_utils
    ----------------

    Test suite for rauth.utils.
'''

from base import RauthTestCase
from rauth.utils import (absolute_url, CaseInsensitiveDict,
                         parse_utf8_qsl, OAuth1Auth, OAuth2Auth)
from requests import Request


class UtilsTestCase(RauthTestCase):
    def test_absolute_url(self):
        self.assertTrue(absolute_url('http://example.com/'))

    def test_absolute_url_https(self):
        self.assertTrue(absolute_url('https://example.com/'))

    def test_not_absolute_url(self):
        self.assertFalse(absolute_url('/some/resource'))

    def test_parse_utf8_qsl(self):
        d = parse_utf8_qsl('fü=bar&rauth=über')
        self.assertEqual(d, {u'rauth': u'\xfcber', u'f\xfc': u'bar'})

    def test_both_kv_unicode(self):
        d = parse_utf8_qsl(u'fü=bar&rauth=über')
        self.assertEqual(d, {u'rauth': u'\xfcber', u'f\xfc': u'bar'})

    def test_rauth_case_insensitive_dict(self):
        d = CaseInsensitiveDict()
        d.setdefault('Content-Type', 'foo')

        d.update({'content-type': 'bar'})

        self.assertEqual(1, len(d.keys()))
        self.assertIn('content-type', d.keys())
        self.assertEqual({'content-type': 'bar'}, d)

        d.update({'CONTENT-TYPE': 'baz'})

        self.assertEqual(1, len(d.keys()))
        self.assertIn('content-type', d.keys())
        self.assertEqual({'content-type': 'baz'}, d)

    def test_rauth_case_insensitive_dict_list_of_tuples(self):
        d = CaseInsensitiveDict([('Content-Type', 'foo')])
        self.assertEqual(d, {'content-type': 'foo'})

    def test_oauth1_auth(self):
        oauth_params = dict(hello='world', foo='bar')

        auth = OAuth1Auth(oauth_params, None)
        r = auth(Request())
        self.assertTrue(r.headers['Authorization'] in
                        ('OAuth realm="",hello="world",foo="bar"',
                         'OAuth realm="",foo="bar",hello="world"'))

        auth = OAuth1Auth(oauth_params, 'example')
        r = auth(Request())
        self.assertTrue(r.headers['Authorization'] in
                        ('OAuth realm="example",hello="world",foo="bar"',
                         'OAuth realm="example",foo="bar",hello="world"'))

    def test_oauth2_auth(self):
        access_token = 'abcdefg'
        auth = OAuth2Auth(access_token)
        r = auth(Request())
        self.assertEqual(r.headers['Authorization'],
                         'Bearer ' + access_token)

    def test_parse_utf8_qsl_with_bytes(self):
        """Test parse_utf8_qsl when parse_qsl returns bytes"""
        from unittest.mock import patch
        from rauth.utils import parse_utf8_qsl

        # Mock parse_qsl to return bytes instead of strings
        with patch('rauth.utils.parse_qsl') as mock_parse_qsl:
            # Simulate Python 2 behavior where parse_qsl returns bytes
            mock_parse_qsl.return_value = [
                (b'f\xc3\xbc', b'bar'),  # 'fü' as bytes
                (b'rauth', b'\xc3\xbcber')  # 'über' as bytes
            ]

            d = parse_utf8_qsl('fü=bar&rauth=über')

            # Should decode bytes to strings
            self.assertEqual(d, {u'fü': u'bar', u'rauth': u'über'})

    def test_parse_utf8_qsl_mixed_bytes_strings(self):
        """Test parse_utf8_qsl with mixed bytes and strings"""
        from unittest.mock import patch
        from rauth.utils import parse_utf8_qsl

        with patch('rauth.utils.parse_qsl') as mock_parse_qsl:
            # Mix of bytes and strings
            mock_parse_qsl.return_value = [
                (b'key1', 'value1'),  # bytes key, string value
                ('key2', b'value2'),  # string key, bytes value
            ]

            d = parse_utf8_qsl('key1=value1&key2=value2')

            self.assertEqual(d, {'key1': 'value1', 'key2': 'value2'})
