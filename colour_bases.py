#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse

foreground_colour = 97
base_colours = {
    'A': 44,
    'C': 41,
    'G': 42,
    'T': 43,
    'U': 45,
    'N': 100,
}

def main(argv=None):
    if argv is None:
        argv = sys.argv

    #prepare description and epilog texts (shown for --help) 
    help_description = 'This script reads lines from STDIN or a file, identifies strings of DNA/RNA and writes coloured output to STDOUT.'

    help_epilog = ''    
    help_epilog += 'examples:\n  head reads.fastq | {}\n  {} genome.fa\n\n'.format(sys.argv[0], sys.argv[0])
    help_epilog += 'colour scheme: \033[{}m'.format(foreground_colour)
    for base in ['A', 'T', 'C', 'G', 'U', 'N']:
        help_epilog += ' \033[{}m {} \033[0m'.format(base_colours[base], base)

    #parse command-line arguments
    parser = argparse.ArgumentParser(description = help_description,
        epilog = help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-w", "--wide",
        help="wide output (add spaces around each base)",
        action='store_true')
    parser.add_argument("file", nargs="?",
        help="file name to read (default: read from STDIN)",
        default='-')
    args = parser.parse_args(argv[1:])

    #open the file if we're not reading from stdin
    if args.file and args.file != '-':
        if args.file.endswith('.gz'):
            import gzip
            file_in = gzip.open(args.file, 'rb')
        else:
            file_in = open(args.file, 'r')
    else:
        file_in = sys.stdin

    #read input line by line (note: this will not work well when streaming long lines)
    try:
        for line in file_in:
            last_match_end = 0
            for match in re.finditer('\\b[ACGTUN]+\\b', line):
                (match_start, match_end) = match.span()

                #write characters before this string
                if match_start > 0:
                    sys.stdout.write(line[last_match_end:match_start])

                #make sure we have the correct foreground colour
                sys.stdout.write('\033[{}m'.format(foreground_colour))

                #loop through bases
                previous_base = ''                
                for i in range(match_start, match_end):
                    base = line[i]
                    
                    #set colour, but only if we have to
                    if base != previous_base:
                        sys.stdout.write('\033[{}m'.format(base_colours[base]))
                        previous_base = base

                    #write base out
                    if args.wide:
                        sys.stdout.write(' {} '.format(base))
                    else:
                        sys.stdout.write(base)

                #remember how far we have written already
                last_match_end = match_end

                #make sure we have default options again
                sys.stdout.write('\033[0m')

            #write the rest of the line
            sys.stdout.write(line[last_match_end:])
    except:
        #try to reset colour settings, even if we are interrupted
        try:
            sys.stdout.write('\033[0m')
            sys.stdout.flush()
        except:
            pass

        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())