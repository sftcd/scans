#!/usr/bin/python
# 
# Copyright (C) 2018 stephen.farrell@cs.tcd.ie
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

# Read a CSV, one (default last) column of which is a domain name, then append
# a bunch of DNS derived values to the row and write out to the output file

import csv
import dns.resolver # install via: sudo apt install python-dnspython; sudo -H pip install dnspython
import pyping # install via: sudo -H pip install pyping

import os, sys, argparse, tempfile, gc
import json
import jsonpickle # install via  "$ sudo pip install -U jsonpickle"
import time, datetime
from dateutil import parser as dparser  # for parsing time from comand line and certs


# command line arg handling 
argparser=argparse.ArgumentParser(description='Read a CSV, one (default last) column of which is a domain name, then append a bunch of DNS derived values to the row and write out to the output file')
argparser.add_argument('-i','--infile',     
                    dest='infile',
                    help='CSV file containing list of domains')
argparser.add_argument('-o','--output_file',     
                    dest='outfile',
                    help='CSV file in which to put records (one per line)')
argparser.add_argument('-c','--col',     
                    dest='col',
                    help='column from input file that has DNS names')
args=argparser.parse_args()

def usage():
    print >>sys.stderr, "usage: " + sys.argv[0] + " -i <in.csv> -o <out.csv> [-c <col1>]"
    print >>sys.stderr, "    read domain names from colum (default: last) of in.csv, do DNS queries and write out to out.csv"
    sys.exit(1)

if args.infile is None:
    usage()

if args.outfile is None:
    usage()

col=-1
if args.col:
    col=int(args.col)

myResolver = dns.resolver.Resolver() #create a new instance named 'myResolver'

# We need to be root to run the pyping thing (ick)
amRoot=False
if not os.geteuid() == 0:
    amRoot=True

queries = [ "A", "AAAA", "MX", "DS", "CAA", "SPF", "TXT" ]

of=open(args.outfile,'w')
wr=csv.writer(of)

count=0

with open(args.infile, 'r') as f:
    r = csv.reader(f)
    for row in r:
        dom=row[col]
        print "Doing " + dom
        domarr = []
        domarr.append(dom)
        for query in queries: 
            pas = []
            pas.append("ping"+query)
            pasok=False
            domarr.append(query)
            try:
                answer = myResolver.query(dom, query) 
                for rdata in answer: 
                    domarr.append(str(rdata))
                row.append(str(rdata))
                # see if a ping works
                if amRoot and (query == "A" or query == "AAAA"):
                    try: 
                        pa = pyping.ping(str(rdata))
                        if pa.ret_code == 0:
                            pas.append(str(pa.avg_rtt))
                            pasok=True
                        else:
                            pas.append("icmp-bummer-non-exception")
                    except:
                        pas.append("icmp-bummer")
            except:
                domarr.append("bummer")
                row.append('no '+query)
            if pasok:
                domarr.append(pas)
        #print row
        wr.writerow(row)
        count += 1
        if count % 10 == 0:
            print >>sys.stderr, "Did " + str(count) + " last: " + dom

of.close()

