# CSUF-grade-report-scanner
OCR text recognition and validation of the aggregated parts of "Graded Class List" documents

This is written in Python 2.7 and depends on the following Python packages:

    pillow editdistance pytesseract

Within a virtualenv you can install them with

    $ pip install pillow editdistance pytesseract

On a fresh Ubuntu install you may need to install system packages first:

    $ apt install libjpeg-dev libtiff-dev libz-dev tesseract-ocr

https://pypi.python.org/pypi/Pillow/
https://pypi.python.org/pypi/editdistance/
https://pypi.python.org/pypi/pytesseract/

These in turn have their own system package dependencies.
