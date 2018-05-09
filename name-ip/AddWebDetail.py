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

# Read a CSV, one (default last) column of which is a URL, then append
# a bunch of Web derived values to the row and write out to the output 
# file

import csv
import dns.resolver #import the module

import os, sys, argparse, tempfile, gc
import json
import jsonpickle # install via  "$ sudo pip install -U jsonpickle"
import time, datetime
from dateutil import parser as dparser  # for parsing time from comand line and certs
import subprocess

myResolver = dns.resolver.Resolver() #create a new instance named 'myResolver'

# command line arg handling 
argparser=argparse.ArgumentParser(description='Read a CSV, one (default last) column of which is a URL, then append a bunch of Web derived values to the row and write out to the output file')
argparser.add_argument('-i','--infile',     
                    dest='infile',
                    help='CSV file containing list of domains')
argparser.add_argument('-o','--output_file',     
                    dest='outfile',
                    help='CSV file in which to put records (one per line)')
argparser.add_argument('-c','--col',     
                    dest='col',
                    help='column from input file that has the URL')
args=argparser.parse_args()

def usage():
    print >>sys.stderr, "usage: " + sys.argv[0] + " -i <in.csv> -o <out.csv> [-c <col1>]"
    print >>sys.stderr, "    Read a CSV, one (default last) column of which is a URL, then append a "
    print >>sys.stderr, "    bunch of Web derived values to the row and write out to the output file"
    sys.exit(1)

if args.infile is None:
    usage()

if args.outfile is None:
    usage()

col=-1
if args.col:
    col=int(args.col)

of=open(args.outfile,'w')
wr=csv.writer(of)

count=0

# encoder options
jsonpickle.set_encoder_options('json', sort_keys=True, indent=2)
jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=2)

# default timeout for zgrab, in seconds
ztimeout=' --timeout 2'
# port parameters
pparms={ 
        '80': '-port 80',
        '443-no-sni': '--port 443 --lookup-domain --tls',
        '443': '-port 443 -tls',
        }

with open(args.infile, 'r') as f:
    r = csv.reader(f)
    for row in r:
        url=row[col]
        if url is None or url=='':
            # add dummy cols to row, not sure how many yet
            pass
        else:
            print "Doing " + url
            # figure hostname from url
            # and figure pathname from url
            hoststart=url.find("//")+1
            hostend=url.find("/",hoststart+1)
            if hostend==-1:
                host=url[hoststart:]
                path='/'
            else:
                host=url[hoststart:hostend]
                path=url[hostend:]
            #print str(hoststart), str(hostend), host, path
            # figure IP addr from hostname
            answer = myResolver.query(host, "A") 
            for rdata in answer: 
                #pick last one
                addr=rdata
            #print "addr: " + str(addr)
            # do HTTP, then HTTP and TLS with SNI, then HTTP and TLS without SNI
            for port in [ "80", "443", "443-no-sni" ]:
                try:
                    cmd='zgrab '+  pparms[port] + " -http " + path + " " + ztimeout
                    #print "cmd: " + cmd
                    proc=subprocess.Popen(cmd.split(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    # 443 is different due to SNI, need to provide host, not address
                    if port=='443-no-sni':
                        #print "doing: port: " + port + " |" + host + "| " + cmd
                        # man it took me a while to figure that "\n" below was needed;-(
                        pc=proc.communicate(input=host + "\n")
                    else:
                        #print "doing: port: " + port + " |" + str(addr) + "| " + cmd
                        pc=proc.communicate(input=str(addr).encode())
                    lines=pc[0].split('\n')
                    #print "pc: " + str(pc)
                    jinfo=json.loads(lines[1])
                    jres=json.loads(lines[0])
                    print jsonpickle.encode(jres)
                    if port=='80':
                        # store at least http response code
                        pass
                    elif port=='443-no-sni':
                        pass
                    elif port=='443':
                        #print lines
                        pass

                except Exception as e:
                    print >>sys.stderr, sys.argv[0] + " exception:" + str(e)
        #print row
        wr.writerow(row)
        count += 1
        sys.exit(0)
        if count % 10 == 0:
            print >>sys.stderr, "Did " + str(count) + " last: " + url
            # debug exit
            sys.exit(0)

of.close()

