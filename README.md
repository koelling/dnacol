# dnacol.py
Color DNA/RNA bases in terminal output

## About
This is a script to display colored DNA or RNA sequences in the terminal. It will read lines from STDIN or a file name provided as an optional command line argument, look for any strings of `[ACGTUN]+` and color them.

## Options
    -w, --wide  Wide output (add spaces around each base)

## Examples
    #read gzipped file
    ./dnacol.py examples/phix.fa.gz | head
    
    #pipe from stdin
    head examples/reads.txt | ./dnacol.py --wide
    
    #use `less -R` to display colors in less
    ./dnacol.py examples/phix.fa.gz | less -R

## Screenshot
![Screenshot](screenshot.png?raw=true)