#!/usr/bin/env python3

import urllib.request
import os
import json
import logging
import random
import datetime
import math
import configparser
import pkg_resources

import appdirs


class Slack:
    def __init__(self, token, hook, channel):
        self.token = token
        self.hook = hook
        self.channel = channel

    def say(self, msg):
        req = urllib.request.Request(
            self.hook,
            headers={'Content-type': 'application/json; charset=utf-8',
                     'Authorization': 'Bearer %s' % self.token})
        payload = {
            "username": "coffeeconnection",
            "icon_emoji": ":coffee:",
            "channel": self.channel,
            "text": msg,
        }
        urllib.request.urlopen(req, json.dumps(payload).encode('utf-8'))
        # print(msg)

    def alone(self, member):
        self.say("sorry <@%s> you're alone. Next time :-)" % member)

    def match(self, couple, niceities):
        sentence = random.choice(niceities)
        self.say(sentence.format("<@%s>" % couple[0],
                                 "<@%s>" % couple[1]))

    def get_slack_members(self):
        req = urllib.request.Request(
            'https://slack.com/api/channels.info?channel=%s' % self.channel,
            headers={'Content-type': 'application/json; charset=utf-8',
                     'Authorization': 'Bearer %s' % self.token})
        resp = urllib.request.urlopen(req)
        channel_info = json.loads(resp.read())
        return channel_info['channel']['members']


def is_off(today):
    return today.strftime("%w") == "6" or today.strftime("%w") == "0"


def need_reset(today, epoch, week_period):
    return (today - epoch).days % (week_period * 7) == 0


def dayleft(today, epoch, week_period):
    """ Number of days left in this week_period (eg 1w or 2w)
    This assume epoch start on a Monday (modulo week_period) and Saturday and
    Sunday doesn't count
    """
    nbweekend = int((today - epoch).days / 7)
    return week_period * 5 - \
        (((today - epoch).days - nbweekend * 2) % (week_period * 5))


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
        logging.info("one match today")
    else:
        if nbplayer % 2 != 0:
            if nbplayer == len(queue):
                nbplayer -= 1
            else:
                nbplayer += 1
        logging.info("%s matched today", nbplayer)
        players = queue[:nbplayer]
        queue = queue[nbplayer:]

    matches = []
    while len(players) >= 2:
        matches.append((players.pop(), players.pop()))

    return matches, queue


def coffeeconnection(slack, today, epoch, week_period,
                     hadcoffee_file, niceities):
    if not os.path.exists(hadcoffee_file) or \
       need_reset(today, epoch, week_period):
        logging.info("reset queue")
        open(hadcoffee_file, "w").close()

    if is_off(today):
        logging.info("no coffee today")
        return

    nbdayleft = dayleft(today, epoch, week_period)
    logging.info("%s days left", nbdayleft)

    members = slack.get_slack_members()
    queue = []
    hadcoffee = get_already_had_coffee_members(hadcoffee_file)

    for member in members:
        if member not in hadcoffee:
            logging.info("%s may have a coffee", member)
            queue.append(member)
        else:
            logging.info("%s already had a coffee", member)

    logging.info("number in queue %s", len(queue))
    if not queue:
        return
    elif len(queue) == 1:
        slack.alone(queue[0])
        return

    random.shuffle(queue)

    (matches, queue) = create_matches(queue, nbdayleft)

    for couple in matches:
        slack.match(couple, niceities)
        hadcoffee.append(couple[0])
        hadcoffee.append(couple[1])

    if len(queue) == 1 and nbdayleft == 1:
        slack.alone(queue[0])

    with open(hadcoffee_file, 'w') as fp:
        for coffied in hadcoffee:
            fp.write("%s\n" % coffied)


def main():
    logging.basicConfig(level=logging.DEBUG,
                        filename="coffeeconnection.log",
                        format="%(asctime)s %(levelname)s %(message)s")
    configfile = os.path.join(appdirs.user_config_dir("coffeeconnection"),
                              "coffeeconnection.ini")
    config = configparser.ConfigParser()
    config.read(configfile)

    today = datetime.date.today()
    epoch = datetime.datetime.strptime(config['DEFAULT']['epoch'],
                                       '%Y-%m-%d').date()
    week_period = int(config['DEFAULT']['week_period'])
    hadcoffee_file = config['DEFAULT']['hadcoffee']
    channel = config['DEFAULT']['channel']
    token = config['DEFAULT']['token']
    hook = config['DEFAULT']['hook']

    slack = Slack(token, hook, channel)

    niceities = []
    niceities_file = pkg_resources.resource_filename(__name__, "niceities.txt")
    with open(niceities_file) as niceities:
        niceities = [line.strip() for line in niceities.readlines()
                     if len(line) > 1]

    coffeeconnection(slack, today, epoch, week_period,
                     hadcoffee_file, niceities)


if __name__ == '__main__':
    main()
