#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = "0.3"
setup(
    name = "dnacol",
    version = version,
    packages = find_packages(),

    # metadata for upload to PyPI
    author = "Nils Koelling",
    author_email = "git@nk.gl",
    description = "Pipe output through this script to color DNA/RNA bases in the terminal",
    license = "MIT",
    keywords = "dnacol rnacol rna dna color colour bases console terminal stdout",
    url = "https://github.com/koelling/dnacol/",
    download_url="https://github.com/koelling/dnacol/archive/%s.tar.gz" % version,
    platforms=["any"],

    entry_points={
        'console_scripts': ['dnacol = dnacol.dnacol:main']
    },

    # could also include long_description, download_url, classifiers, etc.
)