from configparser import ConfigParser
import tempfile
from unittest.mock import patch


def mock_config(func):
    def wrapper(*args, **kwargs):
        with tempfile.NamedTemporaryFile() as config_file:
            print("Mock config file {}".format(config_file.name))
            with tempfile.NamedTemporaryFile() as hadcoffee_file:
                print("Mock hadcoffee file {}".format(hadcoffee_file.name))
                with patch(
                    "coffeeconnection.config._get_config_path",
                    return_value=config_file.name,
                ):
                    configparser = ConfigParser()
                    configparser["DEFAULT"] = {
                        "epoch": "2018-06-11",
                        "week_period": 1,
                        "hadcoffee": hadcoffee_file.name,
                        "channel": "slack_channel_id",
                        "token": "slack_token",
                        "hook": "url",
                        "days_off": "",
                        "skip_emoji_list": "",
                    }
                    with open(config_file.name, "w") as config_file_fd:
                        configparser.write(config_file_fd)
                    func(*args, **kwargs)

    return wrapper
