#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 11:58:11 2018

@author: Vilja Hulden

Extract information from the Chronicling America RDF files - each publication title
(identified with an "sn" ID) has an associated RDF file that contains various metadata
about the title.

Among other things, it has (sometimes) a direct link to sws.geonames.org so one can
extract lat/lon. Below, we use that when it is available.
Else, we take the place of publication and use that to query geonames for lat lon
(if success, get the google maps lat lon; if not, try the
wiki one; if still nothing, mark "NOTFOUND".) All lat/lon results are marked with the
source, with the assumption that the RDF ones are most reliable.

Save the URLs for the essays on ChronAm with more information about the SN (essayurl).

Also, get the publication frequency from the moreinfo essays (the
ones behind the essayurls, downloaded separately with dl-addinfohtml.py.)

"""
import os, codecs, re, urllib2
from bs4 import BeautifulSoup

rdfdir = "rdfs/"
#rdfdir = "/Users/vilja/work/research/digital/newspapers-reprints/rdftest/"
writetsv = "sninfo.tsv"
writenotfound = "sngeonotfound.tsv"
htmldir = "moreinfoessays/"


### PRELIMINARIES ####

# Create a list of states that can be used to standardize state markings
statesfile = "/Users/vilja/work/research/digital/useful_lists/states.tsv"

with codecs.open(statesfile,'r',encoding='utf-8') as f:
    statenamelist = f.read().splitlines()
    statenames = [[l.strip() for l in line.split('\t')] for line in statenamelist]

# Use the downloaded moreinfo essays to get publication frequencies into a dictionary
# Dictionary key is sn
freqs = {}
for item in os.listdir(unicode(htmldir,'utf-8')):
    sn = item[:-5] #filename without extension
    with codecs.open(htmldir+item,'r',encoding='utf-8') as f:
        newfile = f.read()
    soup = BeautifulSoup(newfile,"lxml")
    tag = soup.find('dt',string=re.compile('Frequen'))
    if tag: freqbase = tag.find_next_sibling('dd').string
    if freqbase:  freqm = re.match('^([a-zA-z\-]+)',freqbase)
    if freqm:   freq = freqm.group(0)
    else: freq = 'NOTFOUND'
    freqs[sn] = freq


## Construct queries and regexes used below
#http://sws.geonames.org/4259418/about.rdf
#http://www.geonames.org/search.html?q=Emporium%2C+Cameron+County%2C+Pa.&country=
#http://www.geonames.org/search.html?q=Emporium%2C+Cameron+County%2C+Pa.&country=US

popquery1 = "http://www.geonames.org/search.html?q="
popquery2 = "&country=US"

titleregex = re.compile('<dcterms:title>(.*?)\.*</dcterms:title>')
publisherregex = re.compile('<dc:publisher>(.*?)\.*</dc:publisher>')
placeofpubregex = re.compile('<rda:placeOfPublication>(.*?)</rda:placeOfPublication>')
geonamesregex = re.compile('http://sws.geonames.org/.*?/')

latregex = re.compile('<wgs84_pos:lat>([0-9.-]+)')
lonregex = re.compile('<wgs84_pos:long>([0-9.-]+)')

# map resources can be either from Google or Wikipedia in
# sws.geonames.org query, create a regex for each
googlemapregex = re.compile('/maps/google_([0-9.-]+)_([0-9.-]+)\.html')
#example link: /maps/google_30.534_-92.082.html"
wikimapregex = re.compile('/maps/wikipedia_([0-9.-]+)_([0-9.-]+)\.html')
#example link: /maps/wikipedia_36.76_-95.22.html

essayurlbegin = "https://chroniclingamerica.loc.gov/lccn/"

tsv = []
geonotfound = []
for item in os.listdir(unicode(rdfdir,'utf-8')):
    sn = item[:-4] #filename without extension
    print sn
    #reset all
    essayurl = essayurlbegin + sn + '/'
    geourl = ""
    geourl2 = ""
    lat = ""
    lon = ""
    placeofpub = ""
    hitspage = ""
    state = ""
    city = ""
    with codecs.open(rdfdir+item, 'r', encoding='utf-8') as f:
        newrdf = f.read()
    titlem = titleregex.search(newrdf)
    if titlem: title = titlem.group(1)
    else: title = "NOTFOUND"
    publisherm = publisherregex.search(newrdf)
    if publisherm: publisher = publisherm.group(1)
    else: publisher = "NOTFOUND"
    placeofpubm = placeofpubregex.search(newrdf)
    # a few extra steps with place of publication
    # so as to get city and state separately

    if placeofpubm:
        placeofpubbase = placeofpubm.group(1)
        #sometimes there's a ; at the end that confuses things
        if ';' in placeofpubbase:
            placeofpubbase = re.sub('\s*;','',placeofpubbase)
        # sometimes there are [i.e.] clarifications of places that
        # ... could be useful but they are too few in practice to
        # ... start messing with, easier to fix manually afterward
        # sometimes there are random [] that can just be removed
        # ... otherwise they confuse things
        placeofpubb = re.sub('\[',',',placeofpubbase)
        placeofpubb = re.sub('\]','',placeofpubb)
        placeofpubb = re.sub('\s,',', ',placeofpubb)
        placelist = [it.strip() for it in placeofpubb.split(',')]
        stateb = placelist[-1]
        stfound = False #to see if any states matched
        for stlist in statenames:
            if stateb.strip() in stlist:
                state = stlist[0]
                city = placelist[0]
                placeofpub = city + ", " + state
                stfound = True
        if not stfound:
            placeofpub = placeofpubb
    else:
        placeofpub = 'NOTFOUND'

    geourlmatch = geonamesregex.search(newrdf)
    if geourlmatch:
        geourl = geourlmatch.group(0)
        geourl2 = ""
        geordflink = geourl + 'about.rdf'
        geordf = urllib2.urlopen(geordflink).read()
        lat = latregex.search(geordf).group(1)
        lon = lonregex.search(geordf).group(1)
        geonote = 'RDF'
    else:
        popurlplace = re.sub(',','%2C',placeofpub)
        popurlplace = re.sub('\s+','+',popurlplace)
        popqueryurl = popquery1 + popurlplace + popquery2
        hitspage = urllib2.urlopen(popqueryurl).read()
        latlonmatch =  googlemapregex.search(hitspage)
        latlonmatch2 = wikimapregex.search(hitspage)
        if latlonmatch:
            lat =latlonmatch.group(1)
            lon = latlonmatch.group(2)
            geonote = 'QUERIED, found'
            geourl = popqueryurl
            geourl2 = latlonmatch.group(0)
        elif latlonmatch2:
            lat = latlonmatch2.group(1)
            lon = latlonmatch2.group(2)
            geonote = 'QUERIED, wiki'
            geourl = popqueryurl
            geourl2 = wikimapregex.search(hitspage).group(0)
        else:
            geonotfound.append([sn,placeofpub,popqueryurl])
            geonote = 'NOTFOUND'
            geourl = ''
    #finally, get publication frequency from the dictionary created above
    pubfreq = freqs.get(sn, 'UNKNOWN')

    line = [sn,title,pubfreq,publisher,city,state,placeofpub,lat,lon,geonote,geourl,geourl2,essayurl]
    tsv.append(line)

tsvnew = []
for line in tsv:
    line = [re.sub('&amp;','&',it) for it in line]
#    line = [re.sub('"','',it) for it in line]
#    line = [re.sub("'",'',it) for it in line]
    tsvnew.append(line)

tsvtxt = '\n'.join(['\t'.join(it) for it in tsvnew])
notfoundtxt ='\n'.join(['\t'.join(it) for it in geonotfound])

with codecs.open(writetsv,'w',encoding='utf-8') as f:
    f.write(tsvtxt)

with codecs.open(writenotfound,'w',encoding='utf-8') as f:
    f.write(notfoundtxt)
