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

# take two csvs, join them on column n, and write to output 
# Usually we'll then use awk to select the columns we wanna keep for later

import os, sys, argparse, tempfile, gc
import json
import jsonpickle # install via  "$ sudo pip install -U jsonpickle"
import time, datetime
from dateutil import parser as dparser  # for parsing time from comand line and certs

# command line arg handling 
argparser=argparse.ArgumentParser(description='take two csvs, join them on columns c,d and write to output') 
argparser.add_argument('-1','--in1',     
                    dest='in1',
                    help='file containing list of IPs')
argparser.add_argument('-2','--in2',     
                    dest='in2',
                    help='file containing list of IPs')
argparser.add_argument('-o','--output_file',     
                    dest='outfile',
                    help='file in which to put json records (one per line)')
argparser.add_argument('-c','--c1',     
                    dest='c1',
                    help='column from input file 1 to use for join')
argparser.add_argument('-d','--c2',     
                    dest='c2',
                    help='column from input file 2 to use for join')
args=argparser.parse_args()


def usage():
    print >>sys.stderr, "usage: " + sys.argv[0] + " -1 <csv1> -2 <csv2> [-c <col1>] [-d <col2> -o <outfile>"
    print >>sys.stderr, "   Join two CSV files on columns c1/c2 (default zero for both)"
    sys.exit(1)

if args.in1 is None:
    usage()

if args.in2 is None:
    usage()

if args.outfile is None:
    usage()

# the column of the CSV file that contains the pre-record keyword (zero
# being the first column)
jc1=0
if args.c1 is not None:
    jc1=int(args.c1)
jc2=0
if args.c2 is not None:
    jc2=int(args.c2)

# code below is based on:
# https://stackoverflow.com/questions/20414562/python-joining-csv-files-where-key-is-first-column-value
import csv
from collections import OrderedDict

with open(args.in1, 'r') as f:
    r = csv.reader(f)
    dict1 = OrderedDict((row[jc1], row[0:]) for row in r)

with open(args.in2, 'r') as f:
    r = csv.reader(f)
    dict2 = OrderedDict((row[jc2], row[0:]) for row in r)

result = OrderedDict()
for d in (dict1, dict2):
    for key, value in d.iteritems():
        result.setdefault(key, []).extend(value)

with open(args.outfile, 'w') as f:
    w = csv.writer(f)
    for key, value in result.iteritems():
        w.writerow([key] + value)
