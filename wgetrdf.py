#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 11:49:06 2018

@author: Vilja Hulden

Create wget to get RDF files for sns from Chronicling America

The assumption is that one has a file, uniquesns.txt, which contains
the list of SN ids for the newspaper titles one is interested in.

The relevant RDFs can then be downloaded with wget -i wgetrdfs.txt
"""

import codecs

snfile = "uniquesns.txt"
wgetfile = "wgetrdfs.txt"

with codecs.open(snfile,'r',encoding='utf-8') as f:
    sns = f.read().splitlines()

urlbase = "https://chroniclingamerica.loc.gov/lccn/"
#"https://chroniclingamerica.loc.gov/lccn/sn85038615.rdf"
urls = []
for sn in sns[1:]: #because first line is total count
    url = urlbase + sn + ".rdf"
    urls.append(url)

urltxt = '\n'.join(urls)

with codecs.open(wgetfile,'w',encoding='utf-8') as f:
    f.write(urltxt)
