#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
setup(
    name = "dnacol",
    version = "0.2.1",
    packages = find_packages(),
    scripts = ['dnacol'],

    # metadata for upload to PyPI
    author = "Nils Kölling",
    author_email = "git@nk.gl",
    description = "Pipe output through this script to color DNA/RNA bases in the terminal",
    license = "MIT",
    keywords = "dnacol rnacol rna dna color",
    url = "https://github.com/koelling/dnacol/",

    # could also include long_description, download_url, classifiers, etc.
)