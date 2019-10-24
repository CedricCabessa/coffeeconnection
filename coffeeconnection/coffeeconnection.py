#!/usr/bin/env python3

import urllib.request
import os
import json
import logging
import random
import datetime
import math
import pkg_resources

from coffeeconnection.logger import LOGGER, setup_logger
from coffeeconnection.config import Configuration


def get_niceties():
    niceties_file = pkg_resources.resource_filename(__name__, "niceties.txt")
    with open(niceties_file) as niceties:
        return [line.strip() for line in niceties.readlines() if len(line) > 1]


class Slack:
    def __init__(self, config):
        self.config = config

    def _get_headers(self):
        return {
            "Content-type": "application/json; charset=utf-8",
            "Authorization": "Bearer {}".format(self.config.token),
        }

    def say(self, msg):
        req = urllib.request.Request(self.config.hook, headers=self._get_headers())
        payload = {
            "username": "coffeeconnection",
            "icon_emoji": ":coffee:",
            "channel": self.config.channel,
            "text": msg,
        }
        urllib.request.urlopen(req, json.dumps(payload).encode("utf-8"))

    def match(self, couple, niceties):
        sentence = random.choice(niceties)
        self.say(sentence.format("<@%s>" % couple[0], "<@%s>" % couple[1]))

    def __slack_request(self, endpoint):
        req = urllib.request.Request(
            "https://slack.com/api/{}".format(endpoint), headers=self._get_headers()
        )
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode("utf-8"))

    def get_slack_members(self):
        data_users = self.__slack_request("users.list")
        deads = []
        for member in data_users["members"]:
            if (
                member["deleted"]
                or member["is_bot"]
                or member["profile"]["status_emoji"] in self.config.skip_emoji_list
            ):
                deads.append(member["id"])

        channel_info = self.__slack_request(
            "channels.info?channel={}".format(self.config.channel)
        )
        members = []
        for member in channel_info["channel"]["members"]:
            if member not in deads:
                members.append(member)
            else:
                LOGGER.info("%s is not available", member)
        return members


def is_off(today, days_off):
    return (
        today.strftime("%w") == "6"  # Saturday
        or today.strftime("%w") == "0"  # Sunday
        or today.strftime("%Y-%m-%d") in days_off
    )


def need_reset(today, epoch, week_period):
    return (today - epoch).days % (week_period * 7) == 0


def dayleft(today, epoch, week_period):
    """ Number of days left in this week_period (eg 1w or 2w)
    This assume epoch start on a Monday (modulo week_period) and Saturday and
    Sunday doesn't count
    """
    nbweekend = int((today - epoch).days / 7)
    return week_period * 5 - (
        ((today - epoch).days - nbweekend * 2) % (week_period * 5)
    )


def get_already_had_coffee_members(filepath):
    hadcoffee = []
    with open(filepath) as fp:
        hadcoffee = [line.strip() for line in fp.readlines()]
    return hadcoffee


def create_matches(queue, nbdayleft):
    """ return a list of tuple and the modified queue
    """
    nbplayer = math.ceil(len(queue) / nbdayleft)

    if nbplayer == 1:
        players = queue[:2]
        queue = queue[2:]
        LOGGER.info("one match today")
    else:
        if nbplayer % 2 != 0:
            if nbplayer == len(queue):
                nbplayer -= 1
            else:
                nbplayer += 1
        LOGGER.info("%s matched today", nbplayer)
        players = queue[:nbplayer]
        queue = queue[nbplayer:]

    matches = []
    while len(players) >= 2:
        matches.append((players.pop(), players.pop()))

    return matches, queue


def alone(member, memberlist):
    others = memberlist[:]
    others.remove(member)
    other = random.choice(others)
    return (other, member)


def coffeeconnection(slack, config, niceties):
    if not os.path.exists(config.hadcoffee_file) or need_reset(
        config.today, config.epoch, config.week_period
    ):
        LOGGER.info("reset queue")
        open(config.hadcoffee_file, "w").close()

    if is_off(config.today, config.days_off):
        LOGGER.info("no coffee today")
        return

    nbdayleft = dayleft(config.today, config.epoch, config.week_period)
    LOGGER.info("%s days left", nbdayleft)

    members = slack.get_slack_members()
    queue = []
    hadcoffee = get_already_had_coffee_members(config.hadcoffee_file)

    for member in members:
        if member not in hadcoffee:
            LOGGER.info("%s may have a coffee", member)
            queue.append(member)
        else:
            LOGGER.info("%s already had a coffee", member)

    LOGGER.info("number in queue %s", len(queue))
    if not queue:
        return
    elif len(queue) == 1:
        couple = alone(queue[0], members)
        hadcoffee.append(couple[0])
        hadcoffee.append(couple[1])
        slack.match(couple, niceties)
        return

    random.shuffle(queue)

    (matches, queue) = create_matches(queue, nbdayleft)

    hadcoffee_today = []
    for couple in matches:
        slack.match(couple, niceties)
        hadcoffee.append(couple[0])
        hadcoffee.append(couple[1])
        hadcoffee_today.append(couple[0])
        hadcoffee_today.append(couple[1])

    if len(queue) == 1 and nbdayleft == 1:
        LOGGER.info("one leftover %s", queue[0])
        for coffied in hadcoffee_today:
            members.remove(coffied)
        couple = alone(queue[0], members)
        hadcoffee.append(couple[0])
        hadcoffee.append(couple[1])
        slack.match(couple, niceties)

    with open(config.hadcoffee_file, "w") as fp:
        for coffied in hadcoffee:
            fp.write("{}\n".format(coffied))


def main():
    setup_logger()

    try:
        config = Configuration()
        config.load()
        slack = Slack(config)
        niceties = get_niceties()
        coffeeconnection(slack, config, niceties)
        return 0
    except Exception as error:
        LOGGER.error("Error: %s", str(error))
        return 1


if __name__ == "__main__":
    main()
