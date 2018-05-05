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

# I may try re-do this as a bash script and/or with golang, just for
# fun. We'll see.

import os, sys, argparse, tempfile, gc
import csv
import json
import jsonpickle # install via  "$ sudo pip install -U jsonpickle"
import time, datetime
from dateutil import parser as dparser  # for parsing time from comand line and certs

# HTTP GETter
import httplib2

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

# this is for debug
# pretend fetch (did one manually with curl) so's we can debug
# without contantly bothering their web server
def fgc():
    with file('xx') as f:
        s = f.read()
    return s

def usage():
    print >>sys.stderr, "usage: " + sys.argv[0] + " -i <csvin> -o <csvout> [-c <col>] -k <keyword> -u <url>"
    print >>sys.stderr, "   Scrape URLs with substitution"
    print >>sys.stderr, "   csvin is a CSV file the <col> column of which contains values to"
    print >>sys.stderr, "   use in URL to replace the keyword <keyword>"
    sys.exit(1)

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
                    help='column from input file CSV that contains per-record keyword')
argparser.add_argument('-u','--url',     
                    dest='url',
                    help='url containing template string')
argparser.add_argument('-k','--keyword',     
                    dest='keyword',
                    help='keyword within url that is the template string')
argparser.add_argument('-n','--needle',     
                    dest='needle',
                    help='Needle within HTTP response content from which we start to search for mailto and href')
args=argparser.parse_args()

if args.infile is not None:
    infile=args.infile

if args.outfile is not None:
    outfile=args.outfile

if args.url is None:
    usage()

if args.keyword is None:
    usage()

col=0
if args.column is not None:
    col=int(args.column)
    if col <0:
        usage()

urltemplate=args.url
keyword=args.keyword
count=0

try:
    of=open(args.outfile,'w')
    wr=csv.writer(of)
    with open(args.infile, 'r') as f:
        r = csv.reader(f)
        for row in r:
            if count==0:
                # skip header line
                count+=1
                continue
            count+=1
            keyval=row[col]
            # check if we have that file, already, fetch if not
            fname=keyval+".html"
            if os.path.exists(fname):
                print "Reading cached... "+ keyval + ".html"
                cf=open(keyval+".html",'r')
                content=cf.read()
                cf.close()
            else:
                realURL=urltemplate.replace(keyword,keyval)
                print "Fetching... "+ realURL
                # real fetch
                resp, content = httplib2.Http().request(realURL)
                #print resp
                # pretend fetch (did one manually with curl) so's we can debug
                # without contantly bothering their web server
                #content=fgc()
                cf=open(fname,'w')
                cf.write(content)
                cf.close()
            dstart=0
            if args.needle is not None:
                #print "needle: " + args.needle
                dstart=content.find(args.needle)
                if dstart == -1:
                    print "No " + args.needle + "  in " + realURL
                    continue
            # this is specific to what we scrape, no point in generalising too much
            maddr=''
            mstart=content.find('mailto',dstart) 
            #print "mstart: " + str(mstart)
            if mstart != -1:
                som=content[mstart:]
                mend=som.find('"')
                #print "mend: " + str(mend)
                if mend!=-1:
                    maddr=som[7:mend]
                    #print "maddr: " + maddr
            haddr=''
            wstart=content.find('Website',dstart) 
            if wstart != -1:
                emptycheckstr='Website address:</strong><span>-</span>'
                if content[wstart:wstart+len(emptycheckstr)]==emptycheckstr:
                    # it's an empty one
                    pass
                else:
                    hstart=content.find('href="',wstart) 
                    if hstart != -1:
                        soh=content[hstart+6:]
                        #print "hstart:" + str(hstart)
                        hend=soh.find('"')
                        #print "hend: " + str(hend)
                        if mend!=-1:
                            haddr=soh[0:hend]
                            #print "haddr: " + haddr
            # extract domain from haddr or mail, preferring the first
            if haddr != '':
                hoststart=haddr.find('https://')
                if hoststart==-1:
                    # probably http instead of https
                    hoststart=haddr.find('http://')
                    if hoststart!=-1:
                        hoststart+=7
                else:
                    hoststart+=8
                #print "hoststart: " + str(hoststart)
                wwwthere=0
                if hoststart!=-1:
                    wwwthere=haddr.find("www.",hoststart)
                    #print "wwwthere: " + str(wwwthere)
                    if wwwthere!=-1:
                        hoststart+=4
                    hostend=haddr.find("/",hoststart)
                    #print "hostend: " + str(hostend)
                    if hostend==-1:
                        dom=haddr[hoststart:]
                    else:
                        dom=haddr[hoststart:hostend]
                    #print "dom: " + dom
            if haddr=='' and maddr!='':
                # try from maddr
                domstart=maddr.find('@')
                dom=maddr[domstart+1:]
                print "dom from mail: " + dom

            row.append(maddr)
            row.append(haddr)
            row.append(dom)
            print str(count) + ": " + str(row)
            wr.writerow(row)
            # uncomment this to just test the 1st one
            #sys.exit(0)
    of.close()
            
except Exception as e:
    print >>sys.stderr, sys.argv[0] + " exception:" + str(e)


