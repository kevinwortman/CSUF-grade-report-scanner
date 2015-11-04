#!/bin/env python2

import PIL
import csv
import editdistance
import pytesseract
import sys
import zipfile

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
    s = s.replace('l', '1')
    s = s.replace('O', '0')
    s = s.replace('Z', '2')
    return s

def parse_int(s):
    return int(replace_digits(s))

def line_approx_equal(expected, parsed):
    return (editdistance.eval(expected, replace_hard_dashes(parsed)) < MAX_EDIT_DISTANCE)

# returns a list of CSV rows
def scan_image(filename, file_object):
    rows = []

    message("reading '" + filename + "'...\n")

    im = PIL.Image.open(file_object)
    page = 1
    more_pages = True
    while more_pages:
        try:
            im.seek(page - 1)

            message('    page ' + str(page) + ': ')

            text = pytesseract.image_to_string(im)
            lines = text.split('\n')

            year = term = UNDEFINED
            for line in lines:
                got_fall = 'Fall' in line
                got_spring = 'Spring' in line
                got_summer = 'Summer' in line
                if got_fall or got_spring or got_summer:
                    if got_fall:
                        term = 'Fall'
                    elif got_spring:
                        term = 'Spring'
                    else:
                        term = 'Summer'

                    tokens = line.split()
                    for token in tokens:
                        try:
                            year = parse_int(token)
                            break
                        except Exception:
                            pass

                    assert(year != UNDEFINED)
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

    return rows

def scan_zip(zip_path, csv_path):
    rows = [ ['Page', 'Year', 'Term', 'Number',
              'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D',
              'D-', 'F', 'CR', 'NC', 'AU', 'W', 'WU', 'NC', 'I', 'RP', 'RD'], ]

    message('in "' + zip_path + '"...\n')

    z = zipfile.ZipFile(zip_path, 'r')

    for name in z.namelist():
        f = z.open(name)
        rows += scan_image(name, f)
        f.close()

    z.close()

    message("writing '" + csv_path + "'...\n")
    with open(csv_path, 'w') as f:
        w = csv.writer(f)
        w.writerows(rows)

scan_zip(sys.argv[1], 'grade-report.csv')
