# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv

from lxml import etree
from datetime import datetime
from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'rb') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()

                user_data = data.setdefault(user_id, {})
                user_data[date] = {
                    'start': start,
                    'end': end
                }
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

    return data


def get_user_data():
    """
    avatar: https://intranet.stxnext.pl/api/images/users/141

    Returned data structure:

    user_data = {

        'user_id' : { 'user_name' : <name>,
                      'user_avatar' : <avatar_url>
                    },
        ...
    }

    """

    user_data = {}
    with open(app.config['USERS_XML'], 'rb') as xmlfile:
        parser = etree.parse(xmlfile)
        root = parser.getroot()
        host = root.find('server/host').text
        protocol = root.find('server/protocol').text
        for element in root.find('users').iterchildren():
            user_id = int(element.get('id'))
            for child in element:
                if child.tag == "avatar":
                    user_avatar = child.text
                if child.tag == "name":
                    user_name = child.text

            if user_id:
                user_data[user_id] = {
                    'avatar': '{0}://{1}{2}'.format(
                        protocol,
                        host,
                        user_avatar
                    ),
                    'name': user_name
                }
    return user_data
