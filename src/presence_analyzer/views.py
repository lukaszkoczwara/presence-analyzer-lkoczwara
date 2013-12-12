# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import abort
from flask import render_template

from presence_analyzer.main import app
from presence_analyzer import utils
from presence_analyzer import helpers


import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Rendering of the front page.
    """
    return render_template('presence_weekday.html')


@app.route('/mean_time')
def mean_time_page():
    """
    Rendering of mean time page
    """
    return render_template('mean_time_weekday.html')


@app.route('/start_end')
def start_end_page():
    """
    Rendering of start-end page.
    """
    return render_template('presence_start_end.html')


@app.route('/api/v1/users', methods=['GET'])
@helpers.jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = utils.get_data()
    users_data = utils.get_user_data()

    return_data = []
    for i in data.keys():
        user_data = users_data.get(str(i), None)
        if user_data:
            real_user_name = user_data.get('name')
            user_avatar = user_data.get('avatar')
        else:
            real_user_name = "anonymous"
            user_avatar = None

        return_data.append({'user_id': i, 'name': real_user_name, 'avatar': user_avatar})

    return return_data


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@helpers.jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        abort(401, 'User {} not found!'.format(user_id))

    weekdays = helpers.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], helpers.mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@helpers.jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        abort(401, 'User {} not found!'.format(user_id))

    weekdays = helpers.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@helpers.jsonify
def presence_start_end_view(user_id):
    """
    Returns mean arrival and departure time for each weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        abort(401, 'User {} not found!'.format(user_id))

    weekdays = helpers.group_start_end_times_by_weekday(data[user_id])
    result = [
        (
            calendar.day_abbr[weekday], helpers.mean(intervals['start']),
            helpers.mean(intervals['end'])
        )
        for weekday, intervals in weekdays.iteritems()
    ]

    return result
