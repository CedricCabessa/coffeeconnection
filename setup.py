#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="coffeeconnection",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["appdirs"],
    setup_requires=["flake8"],
    entry_points={
        "console_scripts": ["coffeeconnection = coffeeconnection.coffeeconnection:main"]
    },
    include_package_data=True,
    description="Match people for a coffee over slack",
    url="http://github.com/CedricCabessa/coffeeconnection",
    author="Cédric Cabessa",
    author_email="ced@ryick.net",
    license="MIT",
)
