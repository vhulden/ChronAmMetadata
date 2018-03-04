# Using Chronicling America's RDF and "About" HTML files to create a TSV with metadata about specific newspaper titles

The code here creates a TSV file that contains metadata about specific newspaper titles in Chronicling America. 

The list of newspaper titles (identified by sn) is in `uniquesns.txt` - obviously any list of sns should work, this is just the one I used.

The first step is to create the list of RDF files to be downloaded, using `wgetrdf.py`. Next, run `dl-addinfohtml.py` to get the html files provided by Chronicling America that contain more information; this is used to add the publication frequency to the metadata.

The script `rdfprocess.py` then uses these (saved in directories which can be gleaned from the script) to create a TSV file with the following metadata:

`sn,title,pubfreq,publisher,city,state,placeofpub,lat,lon,geonote,geourl,geourl2,essayurl`

The first few are pretty self-explanatory; the geonote records how the lat/lon was obtained (all via sws.geonames.org, but different types of queries depending on what info the rdf contains), the geourls are related to this, and the essayurl simply records the link to Chronicling America's about page for the newspaper title (not really necessary, just for convenience).

Note that the script makes use of the `states.tsv` file which tries to identify variously abbreviated states correctly.

The file `sninfo.tsv` is the result file, included just as a sample of what is supposed to come out at the other end.

All required Python packages should be pretty standard, except maybe [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) (click the link for documentation and installation options).
