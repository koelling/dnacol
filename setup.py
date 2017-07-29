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
    description = "Display FASTA/FASTQ/SAM/VCF files with colored DNA/RNA bases and quality scores in the terminal",
    license = "MIT",
    keywords = "dnacol rnacol rna dna quality phred color colour bases console terminal stdout",
    url = "https://github.com/koelling/dnacol/",
    download_url="https://github.com/koelling/dnacol/archive/%s.tar.gz" % version,
    platforms=["any"],

    entry_points={
        'console_scripts': ['dnacol = dnacol.dnacol:main']
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
    ]
)