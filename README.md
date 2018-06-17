# coffeeconnection
Connect people for a coffee using slack

This script can be use in a daily cronttab to match a pair of 2 people for a
coffee (or any other beverage).

`coffeeconnection` will get all the members of a slack channel, and during a time
period (1w by default), every day a few people will be called to have a coffee
together.

At the end of the week, every members of the channel should have participate to 1
coffee party. (People can join the channel during the week)

## Installation

We use setupttools (feel free to install it with `--user` if you prefer)

```
$ sudo ./setup.py install
```

Write a crontab:

```
$ cat /etc/cron.d/coffeeconnection
0 16 * * 1-5 myuser /usr/local/bin/coffeeconnection
```

## Configuration

You have to copy `coffeeconnection.ini`:

```
$ mkdir -p ~/.config/coffeeconnection/
$ cp coffeeconnection.ini ~/.config/coffeeconnection/coffeeconnection.ini
```

Edit it with your slack credential

## Make it nice to you

The sentences the bot says come from the file `coffeeconnection/niceities.txt`.

You should edit it to make it more fun :-)
