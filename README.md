# dnacol
Color DNA/RNA bases in terminal output

## About
This is a python script to color DNA or RNA sequences in the terminal. It will read lines from STDIN or from a file and color all strings of DNA/RNA it can find.

### Format-specific coloring
By default, `dnacol` will color all strings of `[ACGTUN]+`. However, it will also recognize a few standard file formats and apply more targeting coloring. When reading a file, these formats will automatically be recognized based on their file extensions. When reading from STDIN, `dnacol` will try to identify the format based on the data (only for sam/vcf files). The format can also be specified using the `--format` option.

- SAM format (`--format=sam`, automatically enabled when filename ends in `.sam` or a line matching the SAM format is found)
    + Ignore headers, only color the SEQ column
- FASTQ format (`--format=fastq`, automatically enabled when filename ends in `.fastq` or `.fq`)
    + Only color the second line of every read entry (spanning four lines)
- VCF format (`--format=vcf`, automatically enabled when filename ends in `.vcf` or a VCF header line is found)
    + Ignore comments, only color the REF and ALT column
- FASTA format (`--format=fasta`, automatically enabled when filename ends in `.fasta` or `.fa`)
    + Ignore sequence names

## Options
    -w, --wide
        wide output (add spaces around each base)
    -f FORMAT, --format FORMAT
        file format (auto|text|sam|vcf|fastq|fasta)

## Download/Install
Requires Python 2.7. To install, simply clone this git repository and use the provided `setup.py` script. The `dnacol` script can also be run standalone.

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

## Screenshot
![Screenshot](screenshot.png?raw=true)