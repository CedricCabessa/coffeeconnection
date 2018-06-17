import datetime
import tempfile
import os

from unittest import TestCase
from unittest.mock import MagicMock

from coffeeconnection import coffeeconnection


def date_from_str(datestr):
    return datetime.datetime.strptime(datestr, '%Y-%m-%d').date()


class TestCoffeeConnection(TestCase):
    def test_is_off(self):
        monday = date_from_str('2018-06-11')
        self.assertFalse(coffeeconnection.is_off(monday))
        friday = date_from_str('2018-06-15')
        self.assertFalse(coffeeconnection.is_off(friday))
        saturday = date_from_str('2018-06-16')
        self.assertTrue(coffeeconnection.is_off(saturday))
        sunday = date_from_str('2018-06-17')
        self.assertTrue(coffeeconnection.is_off(sunday))

    def test_need_reset(self):
        epoch = date_from_str('2018-06-11')
        monday = date_from_str('2018-06-11')
        tuesday = date_from_str('2018-06-12')
        monday1w = date_from_str('2018-06-18')
        monday2w = date_from_str('2018-06-25')
        self.assertTrue(coffeeconnection.need_reset(monday, epoch, 2))
        self.assertFalse(coffeeconnection.need_reset(tuesday, epoch, 2))
        self.assertFalse(coffeeconnection.need_reset(monday1w, epoch, 2))
        self.assertTrue(coffeeconnection.need_reset(monday2w, epoch, 2))

    def test_dayleft(self):
        epoch = date_from_str('2018-06-11')
        monday = date_from_str('2018-06-11')
        tuesday = date_from_str('2018-06-12')
        friday = date_from_str('2018-06-15')
        wednesday = date_from_str('2018-06-20')

        self.assertEqual(coffeeconnection.dayleft(monday, epoch, 1), 5)
        self.assertEqual(coffeeconnection.dayleft(tuesday, epoch, 1), 4)
        self.assertEqual(coffeeconnection.dayleft(friday, epoch, 1), 1)
        self.assertEqual(coffeeconnection.dayleft(wednesday, epoch, 1), 3)

    def test_dayleft_2w(self):
        epoch = date_from_str('2018-06-11')
        monday = date_from_str('2018-06-11')
        tuesday = date_from_str('2018-06-12')
        friday = date_from_str('2018-06-15')
        wednesday = date_from_str('2018-06-20')
        friday1w = date_from_str('2018-06-22')
        monday1w = date_from_str('2018-06-25')

        self.assertEqual(coffeeconnection.dayleft(monday, epoch, 2), 10)
        self.assertEqual(coffeeconnection.dayleft(tuesday, epoch, 2), 9)
        self.assertEqual(coffeeconnection.dayleft(friday, epoch, 2), 6)
        self.assertEqual(coffeeconnection.dayleft(wednesday, epoch, 2), 3)
        self.assertEqual(coffeeconnection.dayleft(friday1w, epoch, 2), 1)
        self.assertEqual(coffeeconnection.dayleft(monday1w, epoch, 2), 10)

    def test_create_matches(self):
        matches, queue = coffeeconnection.create_matches(
            ["a", "b", "c", "d"], 2)
        self.assertEqual(len(queue), 2)
        self.assertEqual(len(matches), 1)

        matches, queue = coffeeconnection.create_matches(
            ["a", "b", "c", "d", "e"], 5)
        self.assertEqual(len(queue), 3)
        self.assertEqual(len(matches), 1)

        matches, queue = coffeeconnection.create_matches(
            ["a", "b", "c", "d"], 1)
        self.assertEqual(len(queue), 0)
        self.assertEqual(len(matches), 2)

        matches, queue = coffeeconnection.create_matches(
            ["a", "b", "c", "d", "e"], 1)
        self.assertEqual(len(queue), 1)
        self.assertEqual(len(matches), 2)

    def test_main_23(self):
        members = [str(i) for i in range(1, 24)]
        slack = coffeeconnection.Slack("", "", "")
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()
        slack.alone = MagicMock()

        epoch = datetime.datetime.strptime('2018-06-11', '%Y-%m-%d').date()
        temp = tempfile.mkstemp()

        today = datetime.datetime.strptime('2018-06-18', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 3)

        today = datetime.datetime.strptime('2018-06-19', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 6)

        today = datetime.datetime.strptime('2018-06-20', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 8)

        today = datetime.datetime.strptime('2018-06-21', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 10)

        self.assertEqual(len(slack.alone.mock_calls), 0)

        today = datetime.datetime.strptime('2018-06-22', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 11)
        self.assertEqual(len(slack.alone.mock_calls), 1)

        today = datetime.datetime.strptime('2018-06-23', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 11)

        today = datetime.datetime.strptime('2018-06-24', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 11)
        self.assertEqual(len(slack.alone.mock_calls), 1)

        os.close(temp[0])
        os.unlink(temp[1])

    def test_main_30(self):
        members = [str(i) for i in range(1, 31)]
        slack = coffeeconnection.Slack("", "", "")
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()
        slack.alone = MagicMock()

        epoch = datetime.datetime.strptime('2018-06-11', '%Y-%m-%d').date()
        temp = tempfile.mkstemp()

        today = datetime.datetime.strptime('2018-06-18', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 3)

        today = datetime.datetime.strptime('2018-06-19', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 6)

        today = datetime.datetime.strptime('2018-06-20', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 9)

        today = datetime.datetime.strptime('2018-06-21', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 12)

        self.assertEqual(len(slack.alone.mock_calls), 0)

        today = datetime.datetime.strptime('2018-06-22', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 15)

        today = datetime.datetime.strptime('2018-06-23', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 15)

        today = datetime.datetime.strptime('2018-06-24', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 15)

        self.assertEqual(len(slack.alone.mock_calls), 0)

        os.close(temp[0])
        os.unlink(temp[1])

    def test_main_31(self):
        members = [str(i) for i in range(1, 32)]
        slack = coffeeconnection.Slack("", "", "")
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()
        slack.alone = MagicMock()

        epoch = datetime.datetime.strptime('2018-06-11', '%Y-%m-%d').date()
        temp = tempfile.mkstemp()

        today = datetime.datetime.strptime('2018-06-18', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 4)

        today = datetime.datetime.strptime('2018-06-19', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 7)

        today = datetime.datetime.strptime('2018-06-20', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 10)

        today = datetime.datetime.strptime('2018-06-21', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 13)

        self.assertEqual(len(slack.alone.mock_calls), 0)

        today = datetime.datetime.strptime('2018-06-22', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 15)
        self.assertEqual(len(slack.alone.mock_calls), 1)

        today = datetime.datetime.strptime('2018-06-23', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 15)
        self.assertEqual(len(slack.alone.mock_calls), 1)

        today = datetime.datetime.strptime('2018-06-24', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 15)
        self.assertEqual(len(slack.alone.mock_calls), 1)

        os.close(temp[0])
        os.unlink(temp[1])

    def test_main_32(self):
        members = [str(i) for i in range(1, 33)]
        slack = coffeeconnection.Slack("", "", "")
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()
        slack.alone = MagicMock()

        epoch = datetime.datetime.strptime('2018-06-11', '%Y-%m-%d').date()
        temp = tempfile.mkstemp()

        today = datetime.datetime.strptime('2018-06-18', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 4)

        today = datetime.datetime.strptime('2018-06-19', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 7)

        today = datetime.datetime.strptime('2018-06-20', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 10)

        today = datetime.datetime.strptime('2018-06-21', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 13)

        today = datetime.datetime.strptime('2018-06-22', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 16)

        today = datetime.datetime.strptime('2018-06-23', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 16)

        today = datetime.datetime.strptime('2018-06-24', '%Y-%m-%d').date()
        coffeeconnection.coffeeconnection(slack, today, epoch, 1, temp[1], [""])
        self.assertEqual(len(slack.match.mock_calls), 16)

        self.assertEqual(len(slack.alone.mock_calls), 0)

        os.close(temp[0])
        os.unlink(temp[1])
