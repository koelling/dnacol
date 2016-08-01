import sys
import re

base_colours = {
    'A': 106,
    'C': 101,
    'G': 102,
    'T': 103,
    'U': 45,
    'N': 47,
}

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if ('-h' in argv or '--help' in argv):
        #print help message and exit
        sys.stderr.write('This script will read lines from STDIN, identify strings of DNA/RNA and write coloured output to STDOUT.\n\n')

        sys.stderr.write('Options:\n\t-w, --wide\tWide output (add spaces around each base)\n\n')
        sys.stderr.write('Example:\n\tcat reads.fastq | python {}\n\n'.format(__file__))

        sys.stderr.write('Colour scheme: \033[30m')
        for base in ['A', 'T', 'C', 'G', 'U', 'N']:
            sys.stderr.write(' \033[{}m {} \033[0m'.format(base_colours[base], base))
        sys.stderr.write('\n')

        return 0

    #wide format?
    wide_format = ('-w' in argv or '--wide' in argv)

    #read input line by line (note: this will not work well when streaming long lines)
    try:
        for line in sys.stdin:
            last_match_end = 0
            for match in re.finditer('\\b[ACGTUN]+\\b', line):
                (match_start, match_end) = match.span()

                #write characters before this string
                if match_start > 0:
                    sys.stdout.write(line[last_match_end:match_start])

                #make sure we have a black font
                sys.stdout.write('\033[30m')

                #loop through bases
                previous_base = ''                
                for i in range(match_start, match_end):
                    base = line[i]
                    
                    #set colour, but only if we have to
                    if base != previous_base:
                        sys.stdout.write('\033[{}m'.format(base_colours[base]))
                        previous_base = base

                    #write base out
                    if wide_format:
                        sys.stdout.write(' {} '.format(base))
                    else:
                        sys.stdout.write(base)

                #remember how far we have written already
                last_match_end = match_end

                #make sure we have default options again
                sys.stdout.write('\033[0m')

            #write the rest of the line
            sys.stdout.write(line[last_match_end:])
    except IOError:
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())