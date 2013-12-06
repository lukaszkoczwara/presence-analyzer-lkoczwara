# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, abort

from presence_analyzer.main import app
from presence_analyzer import utils

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/static/presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@utils.jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = utils.get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        abort(401, 'User {} not found!'.format(user_id))

    weekdays = utils.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], utils.mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_start_end_view(user_id):
    """
    Returns mean arrival and departure time for each weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_start_end_times_by_weekday(data[user_id])
    result = [
        (
            calendar.day_abbr[weekday], utils.mean(intervals['start']),
            utils.mean(intervals['end'])
        )
        for weekday, intervals in weekdays.iteritems()
    ]

    return result
