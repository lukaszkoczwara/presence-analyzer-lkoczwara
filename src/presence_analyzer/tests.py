# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
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

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_time_weekday_view(self):
        """
        Test returning mean presence time of valid and invalid user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.content_length, 102)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0], ['Mon', 0])

        # user with id=56 does not exist
        resp = self.client.get('/api/v1/mean_time_weekday/56')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])

    def test_presence_weekday_view(self):
        """
        Test returning total presence time of valid and invalid user.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.content_length, 125)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0], ['Weekday', 'Presence (s)'])

        # user with id=56 does not exist
        resp = self.client.get('/api/v1/presence_weekday/56')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])

    def test_presence_start_end_view(self):
        """
        Test returning total presence time of valid and invalid user.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0], [u'Mon', 0, 0])

        # user with id=56 does not exist
        resp = self.client.get('/api/v1/presence_start_end/56')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(data, [])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_group_by_weekday(self):
        """
        Test grouping of presence entries by weekday.
        """
        data = utils.get_data()
        result = utils.group_by_weekday(data[10])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0], [])
        self.assertIsNotNone(result[1])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])

    def test_seconds_since_midnight(self):
        """
        Test calculation of amount of seconds since midnight.
        """
        time = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        result = utils.seconds_since_midnight(time)
        self.assertEqual(result, 34745)

    def test_interval(self):
        """
        Test calculation of inverval in seconds between
        two datetime.time objects.
        """
        start = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        end = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        result = utils.interval(start, end)
        self.assertEqual(result, 0)

        start = datetime.datetime.strptime('09:39:05', '%H:%M:%S').time()
        end = datetime.datetime.strptime('12:39:05', '%H:%M:%S').time()
        result = utils.interval(start, end)
        self.assertEqual(result, 10800)

    def test_mean(self):
        """
        Test calculation of arithmetic mean.
        Test returning zero for empty lists.
        """
        result = utils.mean([1, 2, 3, 4])
        self.assertEqual(result, 2.5)

        result = utils.mean([])
        self.assertEqual(result, 0)

    def test_group_start_end_times_by_weekday(self):
        """
        Test grouping of start and end times in sec. by weekday.
        """
        data = utils.get_data()
        result = utils.group_start_end_times_by_weekday(data[10])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0], {'start': [], 'end': []})
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
