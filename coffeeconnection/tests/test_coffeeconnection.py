import datetime
import tempfile
import os

from unittest import TestCase
from unittest.mock import MagicMock, patch

from coffeeconnection import coffeeconnection
from coffeeconnection.config import Configuration
from coffeeconnection.tests.mocking import mock_config


def date_from_str(datestr):
    return datetime.datetime.strptime(datestr, "%Y-%m-%d").date()


class TestCoffeeConnection(TestCase):
    def test_is_off(self):
        monday = date_from_str("2018-06-11")
        assert not coffeeconnection.is_off(monday, [])
        friday = date_from_str("2018-06-15")
        assert not coffeeconnection.is_off(friday, [])
        saturday = date_from_str("2018-06-16")
        assert coffeeconnection.is_off(saturday, [])
        sunday = date_from_str("2018-06-17")
        assert coffeeconnection.is_off(sunday, [])

    def test_is_off_holiday(self):
        christmas = date_from_str("2018-12-25")
        wednesday = date_from_str("2018-12-26")
        assert coffeeconnection.is_off(christmas, ["2018-08-15", "2018-12-25"])
        assert not coffeeconnection.is_off(wednesday, ["2018-08-15", "2018-12-25"])

    def test_need_reset(self):
        epoch = date_from_str("2018-06-11")
        monday = date_from_str("2018-06-11")
        tuesday = date_from_str("2018-06-12")
        monday1w = date_from_str("2018-06-18")
        monday2w = date_from_str("2018-06-25")
        assert coffeeconnection.need_reset(monday, epoch, 2)
        assert not coffeeconnection.need_reset(tuesday, epoch, 2)
        assert not coffeeconnection.need_reset(monday1w, epoch, 2)
        assert coffeeconnection.need_reset(monday2w, epoch, 2)

    def test_dayleft(self):
        epoch = date_from_str("2018-06-11")
        monday = date_from_str("2018-06-11")
        tuesday = date_from_str("2018-06-12")
        friday = date_from_str("2018-06-15")
        wednesday = date_from_str("2018-06-20")

        assert coffeeconnection.dayleft(monday, epoch, 1) == 5
        assert coffeeconnection.dayleft(tuesday, epoch, 1) == 4
        assert coffeeconnection.dayleft(friday, epoch, 1) == 1
        assert coffeeconnection.dayleft(wednesday, epoch, 1) == 3

    def test_dayleft_2w(self):
        epoch = date_from_str("2018-06-11")
        monday = date_from_str("2018-06-11")
        tuesday = date_from_str("2018-06-12")
        friday = date_from_str("2018-06-15")
        wednesday = date_from_str("2018-06-20")
        friday1w = date_from_str("2018-06-22")
        monday1w = date_from_str("2018-06-25")

        assert coffeeconnection.dayleft(monday, epoch, 2) == 10
        assert coffeeconnection.dayleft(tuesday, epoch, 2) == 9
        assert coffeeconnection.dayleft(friday, epoch, 2) == 6
        assert coffeeconnection.dayleft(wednesday, epoch, 2) == 3
        assert coffeeconnection.dayleft(friday1w, epoch, 2) == 1
        assert coffeeconnection.dayleft(monday1w, epoch, 2) == 10

    def test_create_matches(self):
        matches, queue = coffeeconnection.create_matches(["a", "b", "c", "d"], 2)
        assert len(queue) == 2
        assert len(matches) == 1

        matches, queue = coffeeconnection.create_matches(["a", "b", "c", "d", "e"], 5)
        assert len(queue) == 3
        assert len(matches) == 1

        matches, queue = coffeeconnection.create_matches(["a", "b", "c", "d"], 1)
        assert len(queue) == 0
        assert len(matches) == 2

        matches, queue = coffeeconnection.create_matches(["a", "b", "c", "d", "e"], 1)
        assert len(queue) == 1
        assert len(matches) == 2

    def test_alone(self):
        members = ["a", "b", "c"]
        couple = coffeeconnection.alone("b", members)
        assert len(members) == 3
        assert len(couple) == 2
        self.assertNotEqual(couple, ("b", "b"))

    @mock_config
    @patch("coffeeconnection.coffeeconnection.get_already_had_coffee_members")
    def test_main_1(self, get_already_had_coffee_members):
        members = ["a", "b", "c"]
        config = Configuration()
        config.load()

        slack = coffeeconnection.Slack(config)
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()
        get_already_had_coffee_members.return_value = ["a", "b"]

        config.today = date_from_str("2018-06-18")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 1

    @mock_config
    def test_main_23(self):
        members = [str(i) for i in range(1, 24)]
        config = Configuration()
        config.load()

        slack = coffeeconnection.Slack(config)
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()

        config.today = date_from_str("2018-06-18")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 3

        config.today = date_from_str("2018-06-19")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 6

        config.today = date_from_str("2018-06-20")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 8

        config.today = date_from_str("2018-06-21")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 10

        config.today = date_from_str("2018-06-22")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 12

        config.today = date_from_str("2018-06-23")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 12

        config.today = date_from_str("2018-06-24")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 12

    @mock_config
    def test_main_30(self):
        members = [str(i) for i in range(1, 31)]
        config = Configuration()
        config.load()

        slack = coffeeconnection.Slack(config)
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()

        config.today = date_from_str("2018-06-18")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 3

        config.today = date_from_str("2018-06-19")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 6

        config.today = date_from_str("2018-06-20")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 9

        config.today = date_from_str("2018-06-21")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 12

        config.today = date_from_str("2018-06-22")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 15

        config.today = date_from_str("2018-06-23")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 15

        config.today = date_from_str("2018-06-24")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 15

    @mock_config
    def test_main_31(self):
        members = [str(i) for i in range(1, 32)]
        config = Configuration()
        config.load()

        slack = coffeeconnection.Slack(config)
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()

        config.today = date_from_str("2018-06-18")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 4

        config.today = date_from_str("2018-06-19")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 7

        config.today = date_from_str("2018-06-20")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 10

        config.today = date_from_str("2018-06-21")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 13

        config.today = date_from_str("2018-06-22")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 16

        config.today = date_from_str("2018-06-23")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 16

        config.today = date_from_str("2018-06-24")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 16

    @mock_config
    def test_main_32(self):
        members = [str(i) for i in range(1, 33)]
        config = Configuration()
        config.load()

        slack = coffeeconnection.Slack(Configuration())
        slack.get_slack_members = MagicMock(return_value=members)
        slack.match = MagicMock()

        config.today = date_from_str("2018-06-18")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 4

        config.today = date_from_str("2018-06-19")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 7

        config.today = date_from_str("2018-06-20")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 10

        config.today = date_from_str("2018-06-21")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 13

        config.today = date_from_str("2018-06-22")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 16

        config.today = date_from_str("2018-06-23")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 16

        config.today = date_from_str("2018-06-24")
        coffeeconnection.coffeeconnection(slack, config, [""])
        assert slack.match.call_count == 16
