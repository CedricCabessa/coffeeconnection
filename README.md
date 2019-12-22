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

Install the dependencies and the package with pipenv.

```
$ pipenv install --deploy --system
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

The sentences the bot says come from the file `coffeeconnection/niceties.txt`.

You should edit it to make it more fun :-)

## Hack

[![Build Status](https://travis-ci.org/CedricCabessa/coffeeconnection.svg?branch=master)](https://travis-ci.org/CedricCabessa/coffeeconnection)

## Development

### Run tests

We use `tox` to run our tests (including static analysis with `flake8` and
coding style)

Run all the test with

```
tox
```

### Coding style

It is handled by [black](https://github.com/psf/black)

To apply it (requires Python >= 3.6):

```bash
pipenv run ci/blackify
```
