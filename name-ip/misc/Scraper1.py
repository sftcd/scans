#!/usr/bin/python

# Copyright (C) 2018 Stephen Farrell, stephen.farrell@cs.tcd.ie
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# scrape a web-site for contact information (DNS namae and mailto)
# we try be generic, but there are limits:-)

import os, sys, argparse, tempfile, gc
import json
import jsonpickle # install via  "$ sudo pip install -U jsonpickle"
import time, datetime
from dateutil import parser as dparser  # for parsing time from comand line and certs

# default values
# the csv file that contains the per-record keyword with which to populate
# the teplate bit of the URL
infile="keyvalues.csv"
# The output file that'll contain the naming information we extract from the
# HTTP response
outfile="name-and-mailto.csv"
# the column of the CSV file that contains the pre-record keyword (zero
# being the first column)
inffileCol=0
# The URL we'll de-reference, after we've replaced the teplate string with
# the per-record keywords
baseURL=""
# The string we use within the URL as the template that's replaced with
# the per-record keyword
templateStr="KEYWORD"
# dns name xpath expr
dnsXpathExpr=""
# mailto xpath expr
mailtoXpathExpr=""

# command line arg handling 
argparser=argparse.ArgumentParser(description='Scrape DNS and mail from enumerable web-site')
argparser.add_argument('-i','--input',     
                    dest='infile',
                    help='file containing list of IPs')
argparser.add_argument('-o','--output_file',     
                    dest='outfile',
                    help='file in which to put json records (one per line)')
argparser.add_argument('-c','--column',     
                    dest='column',
                    help='column from input file CSV that contains per-record keywword')
argparser.add_argument('-u','--url',     
                    dest='url',
                    help='url containing template string')
argparser.add_argument('-k','--keyword',     
                    dest='keyword',
                    help='keyword within url that is the template string')
argparser.add_argument('-d','--dnsxpath',     
                    dest='dnsxp',
                    help='XPath expression to pull out DNS name from HTTP response')
argparser.add_argument('-m','--mailtoxpath',     
                    dest='mailtoxp',
                    help='XPath expression to pull out mailto from HTTP response')
args=argparser.parse_args()

if args.infile is not None:
    infile=args.infile

if args.outfile is not None:
    outfile=args.outfile

print "hi!"
