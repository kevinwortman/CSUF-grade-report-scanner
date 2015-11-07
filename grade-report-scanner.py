#!/bin/env python2

import csv
import editdistance
import subprocess
import sys

VERBOSE = True
UNDEFINED = '?'
SPRING = 'Spring'
FALL = 'Fall'
SUMMER = 'Summer'
PAGE_SEPARATOR = '=' * 79
GRADE_TITLE = 'GRADE BREAKDOWN/PERCENTAGE'
HEADER_ROW = ['Page', 'Year', 'Term', 'Number',
              'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D',
              'D-', 'F', 'CR', 'NC', 'AU', 'W', 'WU', 'NC', 'I', 'RP', 'RD']

def message(s):
    if VERBOSE:
        sys.stdout.write(s)
        sys.stdout.flush()

def replace_digits(s):
    s = s.replace('l', '1')
    s = s.replace('O', '0')
    s = s.replace('z', '2')
    s = s.replace('Z', '2')
    s = s.replace('S', '5')
    return s

def parse_int(s):
    return int(replace_digits(s))

def parse_tally_line(s):
    s = s.replace('.', '')
    return [parse_int(token) for token in s.split()]

def ocr(tiff_path, text_path_basename):
    message('OCRing "' + tiff_path + '" with tesseract...\n')
    subprocess.call(['tesseract',
                     tiff_path,
                     text_path_basename,
                     '-c', 'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890:/.+-%"',
                     '-c', 'include_page_breaks=1',
                     '-c', 'page_separator=' + PAGE_SEPARATOR])

def parse_grades(text_path):
    rows = []
    
    with open(text_path) as f:
        text = f.read()
        
        pages = [page
                 for page in text.split(PAGE_SEPARATOR)
                 if len(page.strip()) > 0]
        
        for page_index in range(len(pages)):
            page = pages[page_index]
            
            lines = page.splitlines()
            lines = [line.strip() for line in lines]
            lines = [line
                     for line in lines
                     if len(line) > 0]

            year = term = UNDEFINED
            for line in lines:
                tokens = line.split()
                if len(tokens) < 2:
                    continue
                
                match = False
                t0, t1 = tokens[0], tokens[1]
                if editdistance.eval(t0, SPRING) <= 1:
                    term = SPRING
                    match = True
                elif editdistance.eval(t0, FALL) <= 1:
                    term = FALL
                    match = True
                elif editdistance.eval(t0, SUMMER) <= 1:
                    term = SUMMER
                    match = True

                if match:
                    year = parse_int(t1)
                    break

            tallies = [UNDEFINED] * 22
            for i in range(len(lines)):
                if editdistance.eval(lines[i], GRADE_TITLE) <= 2:
                    high_grade_line = lines[i+2]
                    low_grade_line = lines[i+5]
                    tallies = parse_tally_line(high_grade_line) + parse_tally_line(low_grade_line)

            rows.append([page_index + 1, year, term] + tallies)
            
    return rows

def tiff_to_csv(tiff_path, csv_path):
    ocr(tiff_path, 'ocr')
    rows = parse_grades('ocr.txt')
    with open(csv_path, 'w') as f:
        w = csv.writer(f)
        w.writerow(HEADER_ROW)
        w.writerows(rows)

def main():
    if len(sys.argv) != 3:
        print('usage:\n')
        print('  python grade-report-scanner.py TIFF_PATH CSV_PATH\n')
        sys.exit(1)

    tiff_to_csv(sys.argv[1], sys.argv[2])

main()
