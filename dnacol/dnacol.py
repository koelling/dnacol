#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse

foreground_color = 97
base_colors = {
    'A': 44,
    'C': 41,
    'G': 42,
    'T': 43,
    'U': 43,
    'N': 100,
}
quality_colors = [31, 33, 34, 36, 32]

#find the spans of specific tab-separated columns in a given line
def find_column_spans(line, columns):
    matches = []

    previous_pos = -1
    column_number = 0
    while True:
        pos = line.find('\t', previous_pos + 1)
        if pos == -1:
            break

        column_number += 1
        if column_number in columns:
            matches.append( (previous_pos + 1, pos, columns[column_number]) )

        previous_pos = pos

    #last (or only) column in the row
    column_number += 1
    if column_number in columns:
        matches.append( (previous_pos + 1, len(line), columns[column_number]) )

    return matches

def detect_quality_encoding(raw_quality_scores):
    #look for phred+33 encoding
    if min(raw_quality_scores) >= 33 and max(raw_quality_scores) <= 74:
        return 33
    #look for phred+64 encoding (can start as low as -5 for solexa)
    elif min(raw_quality_scores) >= 59 and max(raw_quality_scores) <= 105:
        return 64
    else:
        return -1

def set_color(color_code):
    sys.stdout.write('\033[{}m'.format(color_code))

def print_colored_quality_characters(wide, characters, phred_quality_base, raw_scores = None):
    #calculate score as ASCII code minus base
    if raw_scores is not None:
        scores = [score - phred_quality_base for score in raw_scores]
    else:
        scores = [ord(character) - phred_quality_base for character in characters]

    #truncate the scores to make sure we don't get values <0 or >40
    scores = [0 if score < 0 else 40 if score > 40 else score for score in scores]

    #print out the colored characters
    previous_color = None
    for quality_score, quality_character in zip(scores, characters):
        #determine the right color for this score
        my_color = quality_colors[int(round(float(quality_score) / 40 * (len(quality_colors)-1)))]

        #only change color if we have to
        if my_color != previous_color:
            set_color(my_color)
            previous_color = my_color

        #print the original character
        if wide:
            sys.stdout.write(' {} '.format(quality_character))
        else:
            sys.stdout.write(quality_character)

    #reset color at the end
    set_color(0)

def print_colored_dna_characters(wide, characters):
    previous_base = ''                
    for base in characters:
        if base in base_colors:
            #set color, but only if we have to
            if previous_base == '':
                #make sure we have the correct foreground color
                set_color(foreground_color)

            if base != previous_base:
                set_color(base_colors[base])
                previous_base = base
        else:
            #unknown base, reset to default
            if previous_base != '':
                set_color(0)
                previous_base = ''

        #write base out
        if wide:
            sys.stdout.write(' {} '.format(base))
        else:
            sys.stdout.write(base)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    #prepare description and epilog texts (shown for --help) 
    help_description = 'This script reads lines from STDIN or a file, identifies strings of DNA/RNA and phred-encoded quality scores, and writes colored output to STDOUT.'
    help_description += ' When a file name is provided, files ending in .gz will be decompressed on the fly and the file format will be detected based on the extension.'
    help_description += ' In addition, files in SAM or FASTQ format will also be detected based on their content.'

    help_epilog = ''    
    help_epilog += 'examples:\n  head reads.fastq | {}\n  {} genome.fa\n\n'.format(sys.argv[0], sys.argv[0])
    help_epilog += 'color scheme: '
    for base in ['A', 'T', 'C', 'G', 'U', 'N']:
        help_epilog += ' \033[{}m\033[{}m {} \033[0m'.format(foreground_color, base_colors[base], base)

    #parse command-line arguments
    parser = argparse.ArgumentParser(description = help_description,
        epilog = help_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-w", "--wide",
        help="wide output, add spaces around each base",
        action='store_true')
    parser.add_argument("-f", "--format",
        help="file format (auto|text|sam|vcf|fastq|fasta)",
        default='auto')
    parser.add_argument("--debug",
        help="debug mode (raise exceptions)",
        action='store_true')
    parser.add_argument("file", nargs="?",
        help="file name to read (default: read from STDIN)",
        default='-')
    args = parser.parse_args(argv[1:])

    #make sure we handle both upper and lowercase format names
    args.format = args.format.lower()
    if not args.format in ['auto','text','sam','vcf','fastq','fasta']:
        sys.stderr.write('Unexpected format: {} - setting to auto.\n'.format(args.format))
        args.format = 'auto'

    #open the file if we're not reading from stdin
    if args.file and args.file != '-':
        if args.file.endswith('.gz'):
            import gzip
            file_in = gzip.open(args.file, 'rb')
            filename = args.file[:-3]
        else:
            file_in = open(args.file, 'r')
            filename = args.file

        if args.format == 'auto':
            if filename.endswith('.sam'):
                args.format = 'sam'
            elif filename.endswith('.vcf'):
                args.format = 'vcf'
            elif filename.endswith('.fasta') or filename.endswith('.fa'):
                args.format = 'fasta'
            elif filename.endswith('.fastq') or filename.endswith('.fq'):
                args.format = 'fastq'
    else:
        args.file = '-' #make sure this is dash for stdin
        file_in = sys.stdin

    #read input line by line (note: this will not work well when streaming long lines)
    try:
        line_counter = 0
        possible_fastq = True
        phred_quality_base = None

        for line in file_in:
            last_match_end = 0

            #detect VCF header line
            if args.format == 'auto' and args.file == '-':
                if line.startswith('#CHROM\tPOS\tID\tREF\tALT'):
                    args.format = 'vcf'

            #auto-detect FASTQ format
            if args.format == 'auto' and args.file == '-':                
                if possible_fastq:
                    #first row should start with @ (read identifier)
                    if line_counter == 0 and not line.startswith('@'):
                        possible_fastq = False
                    #second row should be DNA
                    elif line_counter == 1 and not re.search(r'^[A-Z]+$', line):
                        possible_fastq = False
                    #third row should start with plus
                    elif line_counter == 2 and not line.startswith('+'):
                        possible_fastq = False
                    #fourth line is quality scores
                    elif line_counter == 3:
                        #at this point we can assume we have fastq
                        args.format = 'fastq'

            #only parse specific lines
            do_search = True
            do_color_quality = False
            if args.format == 'fastq':
                #only color the second line per read (sequence)
                do_search = line_counter % 4 == 1
                #we can also color the quality scores
                do_color_quality = line_counter % 4 == 3
            elif args.format == 'fasta':
                #do not color id rows
                do_search = not line.startswith('>')
            elif args.format == 'vcf':
                #ignore comments
                do_search = not line.startswith('#')
            elif args.format == 'sam':
                #ignore header
                do_search = not line.startswith('@')
                #quality should always be phred+33
                phred_quality_base = 33

            #keep track of line (for fastq files)
            line_counter += 1

            #process the line
            if do_color_quality:
                #get ascii value for each character
                quality_characters = line.rstrip('\r\n')
                raw_quality_scores = [ord(character) for character in quality_characters]

                #try to detect quality base
                if phred_quality_base is None:
                    phred_quality_base = detect_quality_encoding(raw_quality_scores)
                    if phred_quality_base == -1:
                        sys.stderr.write('Detected FASTQ format but encountered unexpecte quality score range: min = {}, max = {}.\n'.format(
                            min(quality_scores), max(quality_scores)))

                #only proceed if we have a proper phred base
                if phred_quality_base > -1:
                    #print the colored scores
                    print_colored_quality_characters(args.wide, quality_characters, phred_quality_base, raw_scores = raw_quality_scores)

                    #print rest of line (eg. \n)
                    if len(quality_characters) < len(line):
                        sys.stdout.write(line[len(quality_characters):])
                #otherwise just print out the line
                else:
                    sys.stdout.write(line)
            elif do_search:
                #auto-detect SAM format
                if args.format == 'auto' and args.file == '-':
                    if possible_sam:
                        #skip headers
                        if not line.startswith('@'):
                            #try to see if this is in SAM format
                            if re.search('^[!-?A-~]{1,254}'+
                                '\t[0-9]+'+
                                '\t.+'+
                                '\t[0-9]+'+
                                '\t[0-9]+'+
                                '\t(\*|([0-9]+[MIDNSHPX=])+)'+
                                '\t.+'+
                                '\t[0-9]+'+
                                '\t[0-9-]+'+
                                '\t(\*|[A-Za-z=.]+)'
                                '\t.+(\t|$)', line
                            ):
                                args.format = 'sam'
                            else:
                                possible_sam = False

                if args.format == 'sam':
                    #only color column #10 (SEQ)
                    matches = find_column_spans(line, {10: 'dna', 11: 'quality'})
                elif args.format == 'vcf':
                    #only color columns #4+5 (REF+ALT)
                    matches = find_column_spans(line, {4: 'dna', 5: 'dna'})
                elif args.format == 'fastq' or args.format == 'fasta':
                    #color the entire line, except the \n at the end
                    matches = [ (0, line.rfind('\n'), 'dna') ]
                else:
                    #search for strings of DNA/RNA in text
                    pattern = '\\b[ACGTUN]+\\b'
                    matches = [match.span(0) + ('dna',) for match in re.finditer(pattern, line)]

                for match_start, match_end, match_type in matches:
                    #write characters before this string
                    if match_start > 0:
                        sys.stdout.write(line[last_match_end:match_start])

                    #determine whether this is a quality or DNA string
                    if match_type == 'quality':
                        print_colored_quality_characters(args.wide, line[match_start:match_end], phred_quality_base)
                    else:
                        print_colored_dna_characters(args.wide, line[match_start:match_end])

                    #remember how far we have written already
                    last_match_end = match_end

                    #make sure we have default options again
                    set_color(0)

                #write the rest of the line
                sys.stdout.write(line[last_match_end:])
            else:
                sys.stdout.write(line)

        #flush output
        sys.stdout.flush()
    except:
        if args.debug:
            raise
        else:
            #try to reset color settings, even if we are interrupted
            try:
                set_color(0)
                sys.stdout.flush()
            except:
                pass

            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())