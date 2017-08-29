``dnacol`` and ``pcol``
========================

Color DNA/RNA bases, protein amino acid codes and quality scores in terminal output

About
-----

This is a python script to color DNA, RNA and protein sequences in the terminal.
If called using ``dnacol``, it will read lines from STDIN or from a file and color all strings of
DNA/RNA it can find. In addition, it can also color phred-encoded
quality scores in FASTQ/SAM files.
If called using ``pcol``, it will instead color protein sequences encoded as amino acid one-letter codes.

Screenshots
~~~~~~~~~~~

.. image:: https://raw.githubusercontent.com/koelling/dnacol/master/screenshots_v0.4.png

Format-specific coloring
~~~~~~~~~~~~~~~~~~~~~~~~

By default, ``dnacol`` will find and color all strings of one or more DNA/RNA letters and
``pcol`` will color all strings of the twenty standard amino acid letters.
However, they will also recognize a few standard file formats and apply more
targeting coloring. When reading a file, these formats will
automatically be recognized based on their file extensions. When reading
from STDIN, ``dnacol`` and ``pcol`` will try to identify the format based on the data
itself (for FASTQ/SAM/VCF files). The format can also be specified using
the ``--format`` option.

-  SAM format (``--format=sam``, automatically enabled when filename
   ends in ``.sam`` or a line matching the SAM format is found)

   -  Ignore headers, color the SEQ column as DNA and the QUAL column as
      quality scores

-  FASTQ format (``--format=fastq``, automatically enabled when filename
   ends in ``.fastq`` or ``.fq`` or the first four lines match the FASTQ
   format)

   -  Color the second line of every read as DNA
   -  Color the fourth line of every read as quality scores

-  VCF format (``--format=vcf``, automatically enabled when filename
   ends in ``.vcf`` or a VCF header line is found)

   -  Ignore comments, only color the REF and ALT column

-  FASTA format (``--format=fasta``, automatically enabled when filename
   ends in ``.fasta`` or ``.fa``)

   -  Ignore sequence identifiers


Colormaps
~~~~~~~~~
The script support different colormaps, which specify a color for each possible letter of the sequence.
These are shown in ``dnacol --help``. When called using ``dnacol``, the script will use the ``dna_brgy`` colormap by default,
while ``pcol`` will use the ``protein`` colormap. You can change the ``dnacol`` colormap using a configuration file (see below).

Options
-------

::

    -w, --wide
        wide output (add spaces around each base)
    -f FORMAT, --format FORMAT
        file format (auto|text|sam|vcf|fastq|fasta)

Configuration
-------------
You can create a configuration file in YAML format called ``/etc/dnacol`` or ``~/.dnacol`` to change the behavior of this script.
At the moment, the only setting available is the colormap to use for DNA sequences.
See see ``dnacol --help`` for examples of the colormaps that are available.

To use the ``gbyr`` instead of the ``brgy`` colormap, set the ``dna_colormap`` option like this:

::
  
  dna_colormap: gbyr

Download/Install
----------------

To install, use ``pip``::

    pip install dnacol

If the system-wide directory is not writable, you can install to your home directory with::

    pip install dnacol --user

Alternatively, you can clone this git
repository and use the provided ``setup.py`` script.

::

    git clone https://github.com/koelling/dnacol.git
    cd dnacol && python setup.py install

``dnacol`` has been tested with Python 2.7 and Python 3.5 and 3.6.

Examples
--------

::

    #read gzipped file
    dnacol examples/phix.fa.gz | head

    #pipe from stdin
    head examples/reads.txt | dnacol --wide

    #use `pcol` for protein sequences
    pcol examples/hras.fa

    #use `less -R` to display colors in less
    dnacol examples/phix.fa.gz | less -R
