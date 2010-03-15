#!/usr/bin/python

import sys
import codecs
import StringIO
import unicodedata
import re
from lxml import etree
from Html import Html


# Use stdin if no filename given on command-line
inFile = sys.stdin
if len(sys.argv) > 1:
    inFile = open( sys.argv[1],"rb" )

with inFile as input:
    bytes = input.read()

encoding = None
if len(sys.argv) > 2:
    encoding = sys.argv[2]

html=Html( bytes, encoding )

if not html.doc or html.doc.getroot() is None:
    print >> sys.stderr, "Error parsing HTML!" 
    exit(1)

root=html.doc.getroot()

# Remove some stuff we don't want.
# 1. MS Office-generated HTML inserts weird processing instructions -- whack em!
# 2. 
etree.strip_elements( root, etree.ProcessingInstruction )

for meta in root.xpath( "/html/head/meta[@http-equiv and @content]" ):
    print >>sys.stderr, "Removing", etree.tostring( meta, encoding=unicode )
    meta.getparent().remove(meta)

for cruft in root.xpath( "//script|//style" ):
    print >>sys.stderr, "Removing", etree.tostring( cruft, encoding=unicode )
    cruft.getparent().remove(cruft)

# Start serializing at the doc.getroot(), not the doc.  Otherwise we
# get a <!DOCTYPE> declaration.  Which we don't want.
#s= etree.tostring( root, pretty_print=False, method="xml", encoding=unicode )
#print s.encode('utf-8')

body=etree.tostring( html.doc.xpath('/html/body')[0], method='text', encoding=unicode )

print html.metas
print " ".join(body.split()).encode('utf-8')
#print "\n".join( map( lambda p: etree.tostring( p, method='text', encoding=unicode ), html.doc.xpath('//p|//div') ) ).encode('utf-8')
