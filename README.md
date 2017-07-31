# dnacol
Color DNA/RNA bases and quality scores in terminal output

## About
This is a python script to color DNA or RNA sequences in the terminal. It will read lines from STDIN or from a file and color all strings of DNA/RNA it can find. In addition, it can also color phred-encoded quality scores in FASTQ/SAM files.

### Format-specific coloring
By default, `dnacol` will color all strings of `[ACGTUN]+`. However, it will also recognize a few standard file formats and apply more targeting coloring. When reading a file, these formats will automatically be recognized based on their file extensions. When reading from STDIN, `dnacol` will try to identify the format based on the data itself (for FASTQ/SAM/VCF files). The format can also be specified using the `--format` option.

- SAM format (`--format=sam`, automatically enabled when filename ends in `.sam` or a line matching the SAM format is found)
    + Ignore headers, color the SEQ column as DNA and the QUAL column as quality scores
- FASTQ format (`--format=fastq`, automatically enabled when filename ends in `.fastq` or `.fq` or the first four lines match the FASTQ format)
    + Color the second line of every read as DNA
    + Color the fourth line of every read as quality scores
- VCF format (`--format=vcf`, automatically enabled when filename ends in `.vcf` or a VCF header line is found)
    + Ignore comments, only color the REF and ALT column
- FASTA format (`--format=fasta`, automatically enabled when filename ends in `.fasta` or `.fa`)
    + Ignore sequence identifiers

## Options
    -w, --wide
        wide output (add spaces around each base)
    -f FORMAT, --format FORMAT
        file format (auto|text|sam|vcf|fastq|fasta)

## Download/Install
Tested with Python 2.7 and Python 3.6. To install, clone this git repository and use the provided `setup.py` script. When installed correctly, `dnacol` will simply be available as `dnacol` in the command line.

    #download
    git clone https://github.com/koelling/dnacol.git

    #install
    cd dnacol && python setup.py install    
    
    #or: install to home directory (if system-wide directory is not writable)
    cd dnacol && python setup.py install --user

## Examples
    #read gzipped file
    dnacol examples/phix.fa.gz | head

    #pipe from stdin
    head examples/reads.txt | dnacol --wide

    #use `less -R` to display colors in less
    dnacol examples/phix.fa.gz | less -R

## Screenshots
![Screenshots](screenshots_v0.3.png?raw=true)