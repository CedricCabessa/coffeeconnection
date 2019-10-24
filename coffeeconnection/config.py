import os
import configparser
import appdirs
import datetime


def _get_config_path():
    return os.path.join(
        appdirs.user_config_dir("coffeeconnection"), "coffeeconnection.ini"
    )


class Configuration:
    def __init__(self):
        self.path = _get_config_path()
        self.today = datetime.date.today()
        self.epoch = None
        self.week_period = None
        self.hadcoffee_file = None
        self.channel = None
        self.token = None
        self.hook = None
        self.days_off = []
        self.skip_emoji_list = []

    def load(self):
        config = configparser.ConfigParser()
        if not config.read(self.path):
            raise Exception("{} cannot be opened".format(self.path))

        try:
            self.epoch = datetime.datetime.strptime(
                config["DEFAULT"]["epoch"], "%Y-%m-%d"
            ).date()
            self.week_period = int(config["DEFAULT"]["week_period"])
            self.hadcoffee_file = config["DEFAULT"]["hadcoffee"]
            self.channel = config["DEFAULT"]["channel"]
            self.token = config["DEFAULT"]["token"]
            self.hook = config["DEFAULT"]["hook"]
        except Exception as error:
            raise Exception("Bad configuration file: {}".format(str(error)))

        self.days_off = config["DEFAULT"].get("days_off", "").split()
        self.skip_emoji_list = config["DEFAULT"].get("skip_emoji_list", "").split()
