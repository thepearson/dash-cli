# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('cwpcli/cwpcli.py').read(),
    re.M
    ).group(1)


with open("readme.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "dash-cli",
    packages = ["dash-cli"],
    entry_points = {
        "console_scripts": ['dash = dash-cli.dash-cli:main']
        },
    version = version,
    description = "Python command line interface to CWP's Dash API.",
    long_description = long_descr,
    author = "Craig Pearson",
    author_email = "thepearson@gmail.com",
    url = "https://github.com/thepearson/cwp-cli",
    )
