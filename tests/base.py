# -*- coding: utf-8 -*-
'''
    rauth.base
    ----------

    Test suite common infrastructure.
'''

import sys
import json

import requests
import unittest

if not hasattr(unittest.TestCase, 'assertIsNotNone'):
    try:
        import unittest2 as unittest
    except ImportError:
        raise RuntimeError('unittest2 is required to run the rauth test suite')

from inspect import stack, isfunction  # NOQA

if sys.version_info >= (3, 3):
    from unittest.mock import Mock
else:
    from mock import Mock  # NOQA
import pytest


class RauthTestCase(unittest.TestCase):
    def setUp(self):
        response = Mock()
        response.content = json.dumps({'status': 'ok'})
        response.headers = {'Content-Type': 'application/json'}
        response.ok = True
        response.status_code = requests.codes.ok
        self.response = response


def parameterize(iterable):
    '''
    Pytest-compatible parameterization decorator.
    Converts nose-style parameterization to pytest.mark.parametrize.
    '''
    def decorated(func):
        # Extract parameter values from the iterable functions
        param_values = []
        for f in iterable:
            if not isfunction(f):
                raise TypeError('Arguments should be wrapped in a function.')
            method, kwargs = f()  # Unpack the tuple returned by the lambda
            param_values.append((method, kwargs))

        # Apply pytest parametrize decorator with correct parameter names
        return pytest.mark.parametrize("method,kwargs", param_values)(func)

    return decorated
