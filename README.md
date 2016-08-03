# dnacol.py
Color DNA/RNA bases in terminal output

## About
This is a script to display colored DNA or RNA sequences in the terminal. It will read lines from STDIN or a file name provided as an optional command line argument, look for any strings of `[ACGTUN]+` and color them.

## Options
    -w, --wide  Wide output (add spaces around each base)

## Examples
    ./dnacol.py examples/phix.fa.gz | head
    head examples/reads.txt | ./dnacol.py --wide

## Screenshot
![Screenshot](screenshot.png?raw=true)