# -*- coding: utf-8 -*-
'''
    rauth.test_session
    ------------------

    Test suite for rauth.session.
'''

from base import RauthTestCase
from rauth.session import OAuth1Session, OAuth2Session, OflySession


import requests

import json

import sys
if sys.version_info >= (3, 3):
    from unittest.mock import patch
else:
    from mock import patch


class RequestMixin(object):
    def assert_ok(self, r):
        self.assertEqual(json.loads(r.content), {'status': 'ok'})

    @patch.object(requests.Session, 'request')
    def test_request(self, mock_request, **kwargs):
        mock_request.return_value = self.response
        self.assert_ok(self.session.request('GET',
                                            'http://example.com/',
                                            **kwargs))


class OAuth1SessionTestCase(RauthTestCase, RequestMixin):
    def setUp(self):
        RauthTestCase.setUp(self)

        self.session = OAuth1Session('123', '345')

    def test_set_url_without_base_url(self):
        """Test _set_url when service has no base_url"""
        # Create a mock service with no base_url
        class MockService:
            base_url = 'http://api.example.com/'

        session = OAuth1Session('123', '456')
        session.service = MockService()  # Service exists but has no base_url
        url = session._set_url('http://example.com/test')
        self.assertEqual(url, 'http://example.com/test')

    def test_set_url_with_absolute_url(self):
        """Test _set_url with absolute URL when service exists"""
        # Create a mock service with base_url
        class MockService:
            base_url = 'http://api.example.com/'

        session = OAuth1Session('123', '456')
        session.service = MockService()

        # Pass an absolute URL - this should hit line 41
        url = session._set_url('https://other.example.com/test')
        self.assertEqual(url, 'https://other.example.com/test')

    def test_set_url_returns_original_url(self):
        """Test _set_url returns original URL when conditions are not met"""
        session = OAuth1Session('123', '456')
        session.service = None  # This will make the condition False

        url = session._set_url('http://example.com/test')
        self.assertEqual(url, 'http://example.com/test')

    def test_set_url_with_relative_url(self):
        """Test _set_url with relative URL when service has base_url"""
        # Create a mock service with base_url
        class MockService:
            base_url = 'http://api.example.com/'

        session = OAuth1Session('123', '456')
        session.service = MockService()

        # Pass a RELATIVE URL - this should hit line 40
        url = session._set_url('users/profile')
        self.assertEqual(url, 'http://api.example.com/users/profile')

    @patch.object(requests.Session, 'request')
    def test_request_with_optional_params(self, mock_request):
        mock_request.return_value = self.response
        params = {'oauth_callback': 'http://example.com/callback'}
        r = self.session.request('GET', 'http://example.com/', params=params)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_optional_params_as_string(self, mock_request):
        mock_request.return_value = self.response
        params = 'oauth_callback=http://example.com/callback'
        r = self.session.request('GET', 'http://example.com/', params=params)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_optional_data_as_string(self, mock_request):
        mock_request.return_value = self.response
        data = 'oauth_callback=http://example.com/callback'
        r = self.session.request('POST', 'http://example.com/', data=data)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_optional_params_with_data(self, mock_request):
        mock_request.return_value = self.response
        data = {'oauth_callback': 'http://example.com/callback'}
        r = self.session.request('POST', 'http://example.com/', data=data)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_header_auth(self, mock_request):
        mock_request.return_value = self.response
        r = self.session.request('GET',
                                 'http://example.com/',
                                 header_auth=True)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_not_alphanumeric_data_as_string(self, mock_request):
        mock_request.return_value = self.response
        data = 'foo=こんにちは世界'
        r = self.session.request('POST', 'http://example.com/', data=data)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_not_alphanumeric_data_as_dict(self, mock_request):
        mock_request.return_value = self.response
        data = {'foo': 'こんにちは世界'}
        r = self.session.request('POST', 'http://example.com/', data=data)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_entity_method_non_form_encoded(self, mock_request):
        """Test entity method with non-form-encoded content type"""
        mock_request.return_value = self.response
        headers = {'Content-Type': 'application/json'}
        r = self.session.request('POST', 'http://example.com/',
                                 headers=headers, data='{"test": "data"}')
        self.assert_ok(r)


class OAuth2SessionTestCase(RauthTestCase, RequestMixin):
    def setUp(self):
        RauthTestCase.setUp(self)

        self.session = OAuth2Session('123', '345')
        self.session_no_creds = OAuth2Session()

    def test_with_credentials(self):
        assert self.session.client_id == '123'
        assert self.session.client_secret == '345'

    def test_without_credentials(self):
        assert self.session_no_creds.client_id is None
        assert self.session_no_creds.client_secret is None

    @patch.object(requests.Session, 'request')
    def test_request_with_string_params(self, mock_request):
        """Test OAuth2Session with string parameters"""
        mock_request.return_value = self.response
        self.session.access_token = 'test_token'
        params = 'param1=value1&param2=value2'
        r = self.session.request('GET', 'http://example.com/', params=params)
        self.assert_ok(r)


class OflySessionTestCase(RauthTestCase, RequestMixin):
    def setUp(self):
        RauthTestCase.setUp(self)

        self.session = OflySession('123', '345')

    def test_request(self):
        return super(OflySessionTestCase, self).test_request(user_id='123')

    @patch.object(requests.Session, 'request')
    def test_request_with_header_auth(self, mock_request):
        mock_request.return_value = self.response
        r = self.session.request('GET',
                                 'http://example.com/',
                                 user_id='123',
                                 header_auth=True)
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_md5(self, mock_request):
        mock_request.return_value = self.response
        r = self.session.request('GET',
                                 'http://example.com/',
                                 user_id='123',
                                 hash_meth='md5')
        self.assert_ok(r)

    @patch.object(requests.Session, 'request')
    def test_request_with_bad_hash_meth(self, mock_request):
        mock_request.return_value = self.response
        with self.assertRaises(TypeError) as e:
            self.session.request('GET',
                                 'http://example.com/',
                                 user_id='123',
                                 hash_meth='foo')
        self.assertEqual(str(e.exception),
                         'hash_meth must be one of "sha1", "md5"')

    @patch.object(requests.Session, 'request')
    def test_request_with_string_params(self, mock_request):
        """Test OflySession with string parameters"""
        mock_request.return_value = self.response
        params = 'param1=value1&param2=value2'
        r = self.session.request('GET', 'http://example.com/',
                                 user_id='123', params=params)
        self.assert_ok(r)
