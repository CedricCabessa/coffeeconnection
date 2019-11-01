#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="coffeeconnection",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["appdirs"],
    entry_points={
        "console_scripts": ["coffeeconnection = coffeeconnection.coffeeconnection:main"]
    },
    include_package_data=True,
    description="Match people for a coffee over slack",
    long_description=open("README.md").read(),
    url="http://github.com/CedricCabessa/coffeeconnection",
    author="Cédric Cabessa",
    author_email="ced@ryick.net",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
