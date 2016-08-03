# dnacol
Color DNA/RNA bases in terminal output

## About
This is a script to display colored DNA or RNA sequences in the terminal. It will read lines from STDIN or a file name provided as an optional command line argument and color DNA/RNA bases.

### Format-specific coloring
By default, `dnacol` will color all strings of `[ACGTUN]+`. However, it can also recognize a few standard file formats and apply more targeting coloring. When reading a file, these formats will automatically be recognized based on their file extension. However, they can also be selected using the `--format` option.

- SAM format (`--format=sam`, automatically enabled when filename ends in `.sam`)
    + Ignore headers, only color the SEQ column
- FASTQ format (`--format=fastq`, automatically enabled when filename ends in `.fastq` or `.fq`)
    + Only color the second line of every read entry (spanning four lines)
- VCF format (`--format=vcf`, automatically enabled when filename ends in `.vcf`)
    + Ignore comments, only color the REF and ALT column
- FASTA format (`--format=fasta`, automatically enabled when filename ends in `.fasta` or `.fa`)
    + Ignore sequence names

## Options
    -w, --wide
        wide output (add spaces around each base)
    -f FORMAT, --format FORMAT
        file format (auto|text|sam|vcf|fastq|fasta)

## Download/Install
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