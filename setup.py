#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

#load version number (can't just import the package since we might miss requirements)
filename = 'dnacol/version.py'
exec(compile(open(filename, "rb").read(), filename, 'exec')) #python2/3 compatible replacement for execfile()

#load long description from readme
with open('README.rst') as f:
    long_description = f.read()

setup(
    name = __title__,
    version = __version__,
    packages = find_packages(),

    # metadata for upload to PyPI
    author = "Nils Koelling",
    author_email = "git@nk.gl",
    description = "Display FASTA/FASTQ/SAM/VCF files with colored DNA/RNA bases and quality scores (`dnacol`) or a protein sequence with colored amino acid codes (`pcol`) in the terminal",
    long_description = long_description,
    license = "MIT",
    keywords = "dnacol rnacol pcol rna dna protein amino acid quality phred color colour bases console terminal stdout",
    url = "https://github.com/koelling/dnacol/",
    download_url="https://github.com/koelling/dnacol/archive/v%s.tar.gz" % __version__,
    platforms=["any"],

    entry_points={
        'console_scripts': [
            'dnacol = dnacol.dnacol:main_dna',
            'pcol = dnacol.dnacol:main_protein'
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    install_requires=[
        'pyyaml',
    ],
)
