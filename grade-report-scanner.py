#!/bin/env python2

import PIL
import csv
import editdistance
import pytesseract
import sys

VERBOSE = True
MAX_EDIT_DISTANCE = 6
UNDEFINED = '?'
HIGH_GRADE_HEADER = 'A+: A: A-: B+: B: B-: C+: C: C-: D+: D:'
LOW_GRADE_HEADER = 'D-: F: CR: NC: AU: W: WU: NC*: I: RP: RD:'

def message(s):
    if VERBOSE:
        sys.stdout.write(s)

def replace_hard_dashes(s):
    return s.replace('\xe2', '-')

def replace_digits(s):
    return s.replace('l', '1').replace('O', '0')

def parse_int(s):
    return int(replace_digits(s))

def line_approx_equal(expected, parsed):
    return (editdistance.eval(expected, replace_hard_dashes(parsed)) < MAX_EDIT_DISTANCE)

def do_everything(tiff_path, csv_path):

    rows = [ ['Page', 'Year', 'Term', 'Number',
              'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D',
              'D-', 'F', 'CR', 'NC', 'AU', 'W', 'WU', 'NC', 'I', 'RP', 'RD'], ]

    message("scanning '" + tiff_path + "'...\n")

    im = PIL.Image.open(tiff_path)
    page = 1
    more_pages = True
    while more_pages:
        try:
            im.seek(page - 1)

            message('page ' + str(page) + ': ')

            text = pytesseract.image_to_string(im)
            lines = text.split('\n')

            year = term = UNDEFINED
            for line in lines:
                if ('Fall' in line) or ('Spring' in line) or ('Summer' in line):
                    term, year = line.split()
                    year = parse_int(year)
                    break

            number = UNDEFINED
            for line in lines:
                if 'CPSC' in line:
                    token = line.split('CPSC')[-1]
                    fixed = replace_digits(replace_hard_dashes(token))
                    tokens = fixed.split('-')
                    number = tokens[1]
                    break

            pass_counts = [UNDEFINED] * 11
            for i in range(len(lines)):
                if line_approx_equal(HIGH_GRADE_HEADER, lines[i]):
                    pass_counts = [parse_int(token) for token in lines[i+1].split()]
                    break

            fail_counts = [UNDEFINED] * 11
            for i in range(len(lines)):
                if line_approx_equal(LOW_GRADE_HEADER, lines[i]):
                    fail_counts = [parse_int(token) for token in lines[i+1].split()]
                    break

            rows.append([page, year, term, number] + pass_counts + fail_counts)

            message(str(year) + ' ' + term + ' ' + number + '\n')

            page += 1

        except EOFError:
            more_pages = False

    im.close()

    message("writing '" + csv_path + "'...\n")
    with open(csv_path, 'w') as f:
        w = csv.writer(f)
        w.writerows(rows)
        
do_everything('DOC.png', 'grade-report.csv')
