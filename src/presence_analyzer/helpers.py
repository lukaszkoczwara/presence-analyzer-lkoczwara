# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

from json import dumps
from functools import wraps
import threading
import time
from flask import Response
import venusian


class memoized(object):

    def __init__(self, cache_time=100):
        self.cache = {}
        self.cache_time = cache_time
        self.lock = threading.Lock()
        self.cache_until = time.time() + cache_time

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            cache_expired = self.cache_until - time.time() <= 0
            with self.lock:
                if args not in self.cache or cache_expired:
                    self.cache[args] = func(*args, **kwargs)
                    self.cache_until = time.time() + self.cache_time
                return self.cache[args]
        return wrapper


# class memoized(object):
# 
#     def __init__(self, cache_time=100):
#         self.cache = {}
#         self.cache_time = cache_time
#         self.lock = threading.Lock()
#         self.cache_until = time.time() + cache_time
# 
#     def __call__(self, func):
#         def callback(scanner, name, ob):
#             def wrapper(*args, **kwargs):
#                 cache_expired = self.cache_until - time.time() <= 0
#                 with self.lock:
#                     if args not in self.cache or cache_expired:
#                         self.cache[args] = func(*args, **kwargs)
#                         self.cache_until = time.time() + self.cache_time
#                     return self.cache[args]
#             scanner.registry.add(name, wrapper)
#         venusian.attach(func, callback)
#         return func



def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def group_start_end_times_by_weekday(items):
    """
    Groups start and end times in sec. by weekday.
    """

    result = {i: {'start': [], 'end': []} for i in range(7)}
    for date, start_end in items.iteritems():
        start = start_end['start']
        end = start_end['end']
        result[date.weekday()]['start'].append(seconds_since_midnight(start))
        result[date.weekday()]['end'].append(seconds_since_midnight(end))
    return result
