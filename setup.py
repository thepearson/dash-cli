# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('dash/cli.py').read(),
    re.M
    ).group(1)

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "dash-cli",
    packages = ["dash"],
    entry_points = {
        "console_scripts": ['dash-cli = dash.cli:main']
        },
    version = version,
    description = "Python command line interface to CWP's Dash API.",
    long_description = long_descr,
    author = "Craig Pearson",
    author_email = "thepearson@gmail.com",
    url = "https://github.com/thepearson/cwp-cli",
    python_requires='>=2.7',
    )
