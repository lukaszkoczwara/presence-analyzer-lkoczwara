# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os
import json
import datetime
import unittest
import mock

from StringIO import StringIO

from presence_analyzer import main, utils, helpers

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)
TEST_USERS_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'users.xml'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def test_mainpage(self):
        """
        Test rendering of main page.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_mean_time_page(self):
        """
        Test rendering of mean_time_page.
        """
        resp = self.client.get('/mean_time')
        self.assertEqual(resp.status_code, 200)

    def test_start_end_page(self):
        """
        Test rendering of start-end page.
        """
        resp = self.client.get('/start_end')
        self.assertEqual(resp.status_code, 200)

    @mock.patch("presence_analyzer.views.utils")
    def test_api_users_valid_user(self, data_mock):
        """
        Test users listing.
        """
        data_mock.get_data.return_value = {
            10: {
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
        data_mock.get_user_data.return_value = {
            10: {
                'avatar': 'http:///api/images/users/170',
                'name': 'Agata Juszczak',
                }
        }
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        print data
        self.assertEqual(len(data), 1)
        self.assertDictEqual(
            data[0],
            {
                'user_id': 10,
                'name': 'Agata Juszczak',
                'avatar': 'http:///api/images/users/170',
            }
        )

    @mock.patch("presence_analyzer.views.utils")
    def test_api_users_invalid_user(self, data_mock):
        """
        Test users listing.
        """
        data_mock.get_data.return_value = {
            10: {
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
        data_mock.get_user_data.return_value = {
            170: {
                'avatar': 'http:///api/images/users/170',
                'name': 'Agata Juszczak',
                }
        }
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 1)
        self.assertDictEqual(
            data[0],
            {
                'user_id': 10,
                'name': 'anonymous',
                'avatar': None,
            }
        )

    @mock.patch("presence_analyzer.views.utils")
    def test_mean_time_weekday_view(self, utils_mock):
        """
        Test returning mean presence time of valid and invalid user.
        """

        utils_mock.get_data.return_value = {
            10: {
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

        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.content_length, 96)
        self.assertEqual(
            resp.data,
            '['
            '["Mon", 0], ["Tue", 30600.0], ["Wed", 29700.0], ["Thu", 0], '
            '["Fri", 0], ["Sat", 0], ["Sun", 0]'
            ']'
        )

        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0], ['Mon', 0])
        self.assertEqual(data[1], ['Tue', 30600.0])

        # user with id=56 does not exist
        resp = self.client.get('/api/v1/mean_time_weekday/423576')
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.content_type, 'text/html')

    @mock.patch("presence_analyzer.views.utils")
    def test_presence_weekday_view(self, utils_mock):
        """
        Test returning total presence time of valid and invalid user.
        """
        utils_mock.get_data.return_value = {
            10: {
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
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.content_length, 121)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0], ['Weekday', 'Presence (s)'])

        # user with id=56 does not exist
        resp = self.client.get('/api/v1/presence_weekday/56')
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.content_type, 'text/html')

    @mock.patch("presence_analyzer.views.utils")
    def test_presence_start_end_view(self, data_mock):
        """
        Test returning start end time of valid and invalid user.
        """
        data_mock.get_data.return_value = {
            10: {
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
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0], [u'Mon', 0, 0])

        # user with id=56 does not exist
        resp = self.client.get('/api/v1/presence_start_end/56')
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.content_type, 'text/html')


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """
    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update(
            {
                'DATA_CSV': TEST_DATA_CSV,
                'USERS_XML': TEST_USERS_XML,
            }
        )

    @mock.patch('presence_analyzer.utils.open', create=True)
    def test_get_user_data(self, mock_open):
        """
        Test test_get_user_data.
        """
        test_lines = u"""
<intranet>
    <server>
        <host>intranet.stxnext.pl</host>
        <port>443</port>
        <protocol>https</protocol>
    </server>
    <users>
        <user id="141">
            <avatar>/api/images/users/141</avatar>
            <name>John Travolta</name>
        </user>
        <user id="176">
            <avatar>/api/images/users/176</avatar>
            <name>Adrian Kruszewski</name>
        </user>
    </users>
</intranet>
"""
        mock_open.return_value.__enter__.return_value = StringIO(test_lines)
        data = utils.get_user_data()

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [141, 176])
        self.assertItemsEqual(data[141].get('name'), 'John Travolta')
        self.assertItemsEqual(data[176].get('name'), 'Adrian Kruszewski')
        self.assertItemsEqual(
            data[141].get('avatar'),
            'https://intranet.stxnext.pl/api/images/users/141'
        )
        self.assertItemsEqual(
            data[176].get('avatar'),
            'https://intranet.stxnext.pl/api/images/users/176'
        )

    @mock.patch("presence_analyzer.utils.csv")
    @mock.patch('presence_analyzer.utils.open', create=True)
    def test_get_data_two_users(self, mock_open, csv_mock):
        """
        Test test_get_data_two_users
        """
        csv_mock.reader.return_value = [
            ['10', '2013-01-01', '07:39:21', '15:23:01'],
            ['11', '2013-01-01', '10:00:00', '16:00:01']
        ]
        data = utils.get_data()

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        self.assertIn(datetime.date(2013, 01, 01), data[10])
        self.assertItemsEqual(data[10][datetime.date(2013, 01, 01)].keys(),
                              ['start', 'end'])
        self.assertEqual(data[10][datetime.date(2013, 01, 01)]['start'],
                         datetime.time(7, 39, 21))

    @mock.patch("presence_analyzer.utils.csv")
    @mock.patch('presence_analyzer.utils.open', create=True)
    def test_invalid_data(self, mock_open, csv_mock):
        """
        Test invalid user.
        """
        csv_mock.reader.return_value = [
            ['sdasfdew', '2013-01-01', '07:39:21', '15:23:01'],
        ]
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertEqual(data, {})

    @mock.patch("presence_analyzer.utils.csv")
    @mock.patch('presence_analyzer.utils.open', create=True)
    def test_get_data_csv_header(self, mock_open, csv_mock):
        """
        Test test_get_data_csv_header
        """
        csv_mock.reader.return_value = [
            ['header'],
            ['10', '2013-01-01', '07:39:21', '15:23:01']
        ]

        data = utils.get_data()

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10])
        self.assertIn(datetime.date(2013, 01, 01), data[10])
        self.assertItemsEqual(data[10][datetime.date(2013, 01, 01)].keys(),
                              ['start', 'end'])
        self.assertEqual(data[10][datetime.date(2013, 01, 01)]['start'],
                         datetime.time(7, 39, 21))

    @mock.patch("presence_analyzer.utils.csv")
    @mock.patch('presence_analyzer.utils.open', create=True)
    def test_get_data_one_user_many_entries(self, mock_open, csv_mock):
        """
        Test test_get_data_one_user_many_entries
        """
        csv_mock.reader.return_value = [
            ['10', '2011-06-01', '08:38:43', '17:19:02'],
            ['10', '2011-06-02', '08:31:51', '16:13:47'],
            ['10', '2011-06-03', '08:26:05', '10:21:44'],
            ['10', '2011-06-06', '08:40:33', '16:37:40'],
            ['10', '2011-06-07', '15:56:10', '17:01:33'],
            ['10', '2011-06-08', '08:45:31', '17:21:25'],
            ['10', '2011-06-09', '08:38:38', '16:34:11'],
            ['10', '2011-06-10', '08:41:13', '16:22:29'],
            ['10', '2011-06-13', '09:57:07', '16:57:04'],
            ['10', '2011-06-14', '08:35:00', '16:55:17'],
            ['10', '2011-06-15', '08:40:46', '17:25:57'],
            ['10', '2011-06-16', '08:16:38', '16:16:55'],
            ['10', '2011-06-17', '08:44:08', '17:04:20'],
            ['10', '2011-06-20', '08:21:16', '16:49:43'],
            ['10', '2011-06-21', '08:38:52', '16:53:31'],
            ['10', '2011-06-22', '08:36:58', '17:37:29'],
            ['10', '2011-06-27', '08:11:44', '17:42:40'],
            ['10', '2011-06-28', '08:22:04', '17:17:21'],
            ['10', '2011-06-29', '08:26:27', '16:34:32'],
            ['10', '2011-06-30', '08:34:01', '17:10:20'],
            ['10', '2011-07-01', '08:36:29', '16:41:45']
        ]

        data = utils.get_data()

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10])
        self.assertEquals(len(data.get(10).keys()), 21)

    @mock.patch("presence_analyzer.utils.csv")
    @mock.patch('presence_analyzer.utils.open', create=True)
    def test_group_by_weekday(self, mock_open, csv_mock):
        """
        Test grouping of presence entries by weekday.
        """
        csv_mock.reader.return_value = [
            ['10', '2011-06-01', '08:38:43', '17:19:02'],
            ['10', '2011-06-02', '08:31:51', '16:13:47'],
            ['10', '2011-06-03', '08:26:05', '10:21:44'],
            ['10', '2011-06-06', '08:40:33', '16:37:40'],
            ['10', '2011-06-07', '15:56:10', '17:01:33'],
            ['10', '2011-06-08', '08:45:31', '17:21:25'],
            ['10', '2011-06-09', '08:38:38', '16:34:11'],
            ['10', '2011-06-10', '08:41:13', '16:22:29'],
            ['10', '2011-06-13', '09:57:07', '16:57:04'],
            ['10', '2011-06-14', '08:35:00', '16:55:17'],
            ['10', '2011-06-15', '08:40:46', '17:25:57'],
            ['10', '2011-06-16', '08:16:38', '16:16:55'],
            ['10', '2011-06-17', '08:44:08', '17:04:20'],
            ['10', '2011-06-20', '08:21:16', '16:49:43'],
            ['10', '2011-06-21', '08:38:52', '16:53:31'],
            ['10', '2011-06-22', '08:36:58', '17:37:29'],
            ['10', '2011-06-27', '08:11:44', '17:42:40'],
            ['10', '2011-06-28', '08:22:04', '17:17:21'],
            ['10', '2011-06-29', '08:26:27', '16:34:32'],
            ['10', '2011-06-30', '08:34:01', '17:10:20'],
            ['10', '2011-07-01', '08:36:29', '16:41:45']
        ]
        data = utils.get_data()
        result = helpers.group_by_weekday(data[10])

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 7)

        # 4 times for 4 Mondays
        self.assertEqual(result[0], [34256, 28627, 25197, 30507])
        self.assertIsNotNone(result[1], [29679, 32117, 3923, 30017])
        self.assertIsNotNone(result[2], [31511, 32431, 31219, 29285, 30954])
        self.assertIsNotNone(result[3], [27716, 30979, 28533, 28817])

    def test_seconds_since_midnight(self):
        """
        Test calculation of amount of seconds since midnight.
        """
        time = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        result = helpers.seconds_since_midnight(time)
        self.assertEqual(result, 34745)

    def test_interval(self):
        """
        Test calculation of interval in seconds between
        two datetime.time objects.
        """
        start = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        end = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        result = helpers.interval(start, end)
        self.assertEqual(result, 0)

        start = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        end = datetime.datetime.strptime('12:39:05', '%H:%M:%S').time()
        result = helpers.interval(start, end)
        self.assertEqual(result, 10800)

    def test_mean(self):
        """
        Test calculation of arithmetic mean.
        Test returning zero for empty lists.
        """
        result = helpers.mean([1, 2, 3, 4])
        self.assertEqual(result, 2.5)

        result = helpers.mean([])
        self.assertEqual(result, 0)

    @mock.patch("presence_analyzer.utils.csv")
    @mock.patch('presence_analyzer.utils.open', create=True)
    def test_group_start_end_times_by_weekday(self, mock_open, csv_mock):
        """
        Test grouping of start and end times in sec. by weekday.
        """
        csv_mock.reader.return_value = [
            ['10', '2011-06-01', '08:38:43', '17:19:02'],
            ['10', '2011-06-02', '08:31:51', '16:13:47'],
            ['10', '2011-06-03', '08:26:05', '10:21:44'],
            ['10', '2011-06-06', '08:40:33', '16:37:40'],
            ['10', '2011-06-07', '15:56:10', '17:01:33'],
            ['10', '2011-06-08', '08:45:31', '17:21:25']
        ]
        data = utils.get_data()
        result = helpers.group_start_end_times_by_weekday(data[10])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0], {'start': [31233], 'end': [59860]})
        self.assertIsNotNone(result[1])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
