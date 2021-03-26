# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='ignorant',
    version="1.1",
    packages=find_packages(),
    author="megadose",
    author_email="megadose@protonmail.com",
    install_requires=["termcolor","bs4","httpx","trio","argparse","tqdm"],
    description="ignorant allows you to check if a phone is used on different sites like snapchat.",
    include_package_data=True,
    url='http://github.com/megadose/ignorant',
    entry_points = {'console_scripts': ['ignorant = ignorant.core:main']},
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
