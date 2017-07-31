#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse
import math

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

def write_colored_quality_characters(wide, characters, phred_quality_base):
    #calculate score as ASCII code minus base
    scores = [ord(character) - phred_quality_base for character in characters]

    #truncate the scores to make sure we don't get values <0 or >40
    scores = [0 if score < 0 else 40 if score > 40 else score for score in scores]

    #write out the colored characters
    previous_color = None
    for quality_score, quality_character in zip(scores, characters):
        #determine the right color for this score
        my_color = quality_colors[int(math.floor(float(quality_score) / 41 * (len(quality_colors))))]

        #only change color if we have to
        if my_color != previous_color:
            set_color(my_color)
            previous_color = my_color

        #write the original character
        if wide:
            sys.stdout.write(' {} '.format(quality_character))
        else:
            sys.stdout.write(quality_character)

    #reset color at the end
    set_color(0)

def write_colored_dna_characters(wide, characters):
    previous_base = ''                
    for base in characters:
        if base in base_colors:
            #set color, but only if we have to
            if previous_base == '':
                #make sure we have the correct foreground color (need to do this inside the loop since we may have reset below)
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

    #in python3 a broken pipe raises BrokenPipeError, but python2 doesn't have that yet
    try:
        broken_pipe_error_class = BrokenPipeError
    except NameError:
        broken_pipe_error_class = IOError #this will be repeated below, but that does not seem to cause any problems

    #prepare description and epilog texts (shown for --help) 
    help_description = 'This script reads lines from STDIN or a file, identifies strings of DNA/RNA and phred-encoded quality scores, and writes colored output to STDOUT.'
    help_description += ' When a file name is provided, files ending in .gz will be decompressed on the fly and the file format will be detected based on the extension.'
    help_description += ' Data in SAM or FASTQ format can also be detected when piped through STDIN.'

    help_epilog = ''    
    help_epilog += 'examples:\n  head reads.fastq | {}\n  {} genome.fa\n\n'.format(sys.argv[0], sys.argv[0])
    help_epilog += 'base color scheme:'
    for base in ['A', 'T', 'C', 'G', 'U', 'N']:
        help_epilog += ' \033[{}m\033[{}m {} \033[0m'.format(foreground_color, base_colors[base], base)
    help_epilog += '\n'
    help_epilog += 'quality color scheme:'
    for quality_score in range(41):
        help_epilog += ' \033[{}m{:02d}\033[0m'.format(quality_colors[int(math.floor(float(quality_score) / 41 * (len(quality_colors))))], quality_score)

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
        help="file name to read (default: - = read from STDIN)",
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
            file_in = gzip.open(args.file, 'rt')
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
        possible_sam = True
        phred_quality_base = None

        for line in file_in:
            last_match_end = 0

            #detect VCF header line
            if args.format == 'auto' and args.file == '-':
                if line.startswith('#CHROM\tPOS\tID\tREF\tALT'):
                    args.format = 'vcf'

            #auto-detect format based on file contents
            if args.format == 'auto' and args.file == '-':
                #auto-detect FASTQ format
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

                #auto-detect SAM format
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
                            #make sure we don't try this for every line
                            possible_sam = False

            #only parse specific lines
            do_search = True
            if args.format == 'fastq':
                #only color the second and fourth line per read (sequence, quality)
                do_search = line_counter % 4 == 1 or line_counter % 4 == 3
            elif args.format == 'fasta':
                #ignore id lines
                do_search = not line.startswith('>')
            elif args.format == 'vcf':
                #ignore comment lines
                do_search = not line.startswith('#')
            elif args.format == 'sam':
                #ignore header lines
                do_search = not line.startswith('@')

                #quality should always be phred+33, according to SAM format specification
                phred_quality_base = 33

            #process the line
            if do_search:
                #figure out which parts of the line to color
                if args.format == 'sam':
                    #only color column #10 (SEQ)
                    matches = find_column_spans(line, {10: 'dna', 11: 'quality'})
                elif args.format == 'vcf':
                    #only color columns #4+5 (REF+ALT)
                    matches = find_column_spans(line, {4: 'dna', 5: 'dna'})
                elif args.format == 'fastq' or args.format == 'fasta':
                    match_type = 'dna'
                    if args.format == 'fastq':
                        if line_counter % 4 == 3:
                            match_type = 'quality'

                    #color the entire line, except the \n at the end
                    line_end = line.find('\n')
                    matches = [ (0, line_end if line_end > 0 else len(line), match_type) ]
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
                        #try to detect quality base
                        if phred_quality_base is None:
                            raw_quality_scores = [ord(character) for character in line[match_start:match_end]]
                            phred_quality_base = detect_quality_encoding(raw_quality_scores)
                            if phred_quality_base == -1:
                                sys.stderr.write('Detected FASTQ format but encountered unexpected quality score range: min = {}, max = {}.\n'.format(
                                    min(raw_quality_scores), max(raw_quality_scores)))

                        if phred_quality_base >= 0:
                            write_colored_quality_characters(args.wide, line[match_start:match_end], phred_quality_base)
                        else:
                            sys.stdout.write(line[match_start:match_end])
                    else:
                        write_colored_dna_characters(args.wide, line[match_start:match_end])

                    #remember how far we have written already
                    last_match_end = match_end

                    #make sure we have default options again
                    set_color(0)

                #write the rest of the line
                sys.stdout.write(line[last_match_end:])
            else:
                sys.stdout.write(line)

            #keep track of line (for fastq files)
            line_counter += 1

        #flush output
        sys.stdout.flush()
    except (IOError, KeyboardInterrupt, broken_pipe_error_class):
        if args.debug:
            raise
        else:
            #try to reset color settings, even if we are interrupted
            try:
                set_color(0)
                sys.stdout.flush()
            except:
                pass

            #then return nonzero exit status
            sys.stderr.close() #this prevents any additional broken pipe errors
            return 1

    sys.stderr.close() #this prevents any additional broken pipe errors
    return 0

if __name__ == "__main__":
    sys.exit(main())