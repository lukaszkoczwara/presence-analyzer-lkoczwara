# -*- coding: utf-8 -*-
"""
Decprators.
"""

import os
import time
import threading

from json import dumps
from functools import wraps
from flask import Response


class memoized(object):
    """
    Decorator used to cache results for certain amount of time.
    Decorator is equipped with 'threading' lock to secure access to the same
    resource by more than one thread.
    """

    def __init__(self, cache_time=100):
        self.cache = {}
        self.cache_time = cache_time
        self.lock = threading.Lock()
        self.cache_until = time.time() + cache_time

    def __call__(self, func):

        # this check is done to return undecorated function for unit tests
        if os.environ.get('TEST', None):
            return func

        def wrapper(*args, **kwargs):
            cache_expired = self.cache_until - time.time() <= 0
            with self.lock:
                if args not in self.cache or cache_expired:
                    self.cache[args] = func(*args, **kwargs)
                    self.cache_until = time.time() + self.cache_time
                return self.cache[args]
        return wrapper


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner
