#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 11:49:06 2018

@author: Vilja Hulden

Download the "more info" pages for all sns to extract the publication frequency
This is basically just a replacement for wget, so as to be able to give the
downloaded files sensible names (pattern: sn.html)
"""

import codecs,urllib2,os

import chardet

# this is copy-pasted from
# https://stackoverflow.com/questions/3683717/urllib2-fetch-and-show-any-language-page-encoding-problem
# seems to work nicely

def fetch(url):
 try:
    result = urllib2.urlopen(url)
    rawdata = result.read()
    encoding = chardet.detect(rawdata)
    return rawdata.decode(encoding['encoding'])

 except urllib2.URLError, e:
    print "Error {}".format(e)

snfile = "uniquesns.txt"
writedir = "moreinfoessays/"
if not os.path.exists(writedir):
    os.makedirs(writedir)

with codecs.open(snfile,'r',encoding='utf-8') as f:
    sns = f.read().splitlines()

urlbase = "https://chroniclingamerica.loc.gov/lccn/"
urls = []
for sn in sns[1:]: #because first line is total count
    url = urlbase + sn + "/"
    urls.append(url)

urltxt = '\n'.join(urls)

snurl = zip(sns[1:],urls)

counter = 1
total = len(snurl)
for sn, url in snurl:
    print "Downloading file {0} of {1}".format(counter,total)
    counter +=1
    html = fetch(url) #see function def above
    fn = writedir+sn+'.html'
    with codecs.open(fn,'w',encoding='utf-8') as f:
        f.write(html)
