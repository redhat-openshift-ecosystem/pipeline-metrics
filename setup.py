#!/usr/bin/python
from setuptools import setup, find_packages


setup(
    name="metrics",
    version="0.0.1",
    author="exd-guild-isv",
    author_email="exd-guild-isv@redhat.com",
    description=("Tekton pipelines metrics"),
    license="GPLv3",
    url="https://gitlab.cee.redhat.com/isv/mercury/mercury/",
    package_dir={"": "."},
    packages=find_packages(".", exclude=("tests",)),
    entry_points={
        "console_scripts": [
            "metrics=metrics.main:main",
        ]
    },
)
