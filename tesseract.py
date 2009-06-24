#!/usr/bin/env python
'''
Python-tesseract is an optical character recognition (OCR) tool for python.
That is, it will recognize and "read" the text embedded in images.

Python-tesseract is a wrapper for google's Tesseract-OCR
( http://code.google.com/p/tesseract-ocr/ ).  Python-tesseract is also useful
as a stand-alone invocation script to tesseract, as it can read all image types
supported by the Python imaging library, including jpeg, png, gif, bmp, tiff,
and others.  Tesseract by default only supports tiff and bmp. Additionally, if
used as a script, Python-tesseract will print the recognized text in stead of
writing it to a file. Support for confidence estimates and bounding box data is
planned for future releases.


USAGE:
From the shell:
 $ ./tesseract.py image.jpeg                # prints recognized text in image
 $ ./tesseract.py -l fra french_image.jpeg  # recognizes french text
In python:
 > from tesseract import image_to_string
 > import Image
 > print image_to_string(Image('image.jpeg'))
 > print image_to_string(Image('french_image.jpeg'), lang='fra')


INSTALLATION:
* Python-tesseract requires python 2.5 or later.
* You will need the Python Imaging Library (PIL).  Under Debian/Ubuntu, this is
  the package "python-imaging".
* Install tesseract-ocr from http://code.google.com/p/tesseract-ocr/ . You must
  be able to invoke the tesseract command as "tesseract". If this isn't the
  case, for example because tesseract isn't in your PATH, you will have to
  change the "tesseract_cmd" variable at the top of 'tesseract.py'.


COPYRIGHT:
Python-tesseract is released under the GPL v3.
Copyright (c) Samuel Hoffstaetter, 2009
http://wiki.github.com/hoffstaetter/python-tesseract


'''

# CHANGE THIS IF TESSERACT IS NOT IN YOUR PATH, OR IS NAMED DIFFERENTLY
tesseract_cmd = 'tesseract'

from __future__ import with_statement
import Image
import StringIO
import subprocess
import sys
import os

__all__ = ['image_to_string']

def run_tesseract(input_filename, output_filename_base, lang=None):
    '''
    runs the command:
        `tesseract_cmd` `input_filename` `output_filename_base`
    
    returns the exit status of tesseract, as well as tesseract's stderr output

    '''

    command = [tesseract_cmd, input_filename, output_filename_base]
    if lang is not None:
        command += ['-l', lang]

    proc = subprocess.Popen(command,
            stderr=subprocess.PIPE)
    return (proc.wait(), proc.stderr.read())

def cleanup(filename):
    ''' tries to remove the given filename. Ignores non-existent files '''
    try:
        os.remove(filename)
    except OSError:
        pass

def get_errors(error_string):
    '''
    returns all lines in the error_string that start with the string "error"

    '''

    lines = error_string.splitlines()
    error_lines = (line for line in lines if line.find('Error') >= 0)
    return '\n'.join(error_lines)

def tempnam():
    ''' returns a temporary file-name '''

    # prevent os.tmpname from printing an error...
    stderr = sys.stderr
    try:
        sys.stderr = StringIO.StringIO()
        return os.tempnam(None, 'tess_')
    finally:
        sys.stderr = stderr

class TesseractError(Exception):
    def __init__(status, message):
        self.status = status
        self.message = message

def image_to_string(image, lang=None):
    '''
    Runs tesseract on the specified image. First, the image is written to disk,
    and then the tesseract command is run on the image. Resseract's result is
    read, and the temporary files are erased.

    '''

    input_file_name = '%s.bmp' % tempnam()
    output_file_name_base = tempnam()
    output_file_name = '%s.txt' % output_file_name_base
    try:
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name, output_file_name_base, lang=lang)
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        with file(output_file_name) as f:
            return f.read().strip()
    finally:
        cleanup(input_file_name)
        cleanup(output_file_name)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python tesseract.py input_file\n')
        exit(1)
    else:
        image = Image.open(sys.argv[1])
        print image_to_string(image)

