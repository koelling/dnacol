# dnacol
Color DNA/RNA bases in terminal output

## About
This is a script to display colored DNA or RNA sequences in the terminal. It will read lines from STDIN or a file name provided as an optional command line argument, look for any strings of `[ACGTUN]+` and color them.

## Options
    -w, --wide  Wide output (add spaces around each base)

## Download/Install
    git clone https://github.com/koelling/dnacol.git
    cd dnacol
    python setup.py install

## Examples
    #read gzipped file
    dnacol examples/phix.fa.gz | head

    #pipe from stdin
    head examples/reads.txt | dnacol --wide

    #use `less -R` to display colors in less
    dnacol examples/phix.fa.gz | less -R

## Screenshot
![Screenshot](screenshot.png?raw=true)