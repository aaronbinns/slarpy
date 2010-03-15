#!/usr/bin/python

# stdlib
import StringIO
import re
import sys
import unicodedata
from datetime import datetime
from urllib2  import Request
from urllib2  import urlopen
from urllib   import unquote_plus
from urlparse import urlsplit
from lxml import etree
# my modules
import superdec
import sniffer
from gunzip       import gunzip
from ArcRecord    import ArcRecord
from HttpResponse import HttpResponse
from Html         import Html
from DefaultTransformer import DefaultTransformer

from optparse import OptionParser

parser=OptionParser( usage='%prog: [options] <file|url> <offset>' )
parser.add_option( '-l', dest='logfile',  metavar='log',  help='append log messages here, default=stderr' )
parser.add_option( '-d', dest='outdir',   metavar='dir',  help='output directory' )
parser.add_option( '-o', dest='outfile',  metavar='file', help='output file' )
parser.add_option( '-t', dest='transform',metavar='trans',help='custom transform file' )
parser.add_option( '-e', dest='encoding', metavar='enc',  help='use this encoding, over-ride all normal rules' )
parser.add_option( '-c', dest='checksum', metavar='sum',  help='checksum for archive record')
parser.add_option( '-i', dest='inputs',   metavar='file', help='read inputs from control file' )

options, args = parser.parse_args()

if options.outfile and options.outdir:
    parser.error('options -d and -o are mutually exclusive')
if options.inputs and (options.encoding or options.outfile or options.checksum or options.transform):
    parser.error('option -i cannot be used with -o, -t, -e, -c')
if options.inputs:
    parser.error('option -i not implemented yet')
elif len(args) != 2:
    parser.print_help()
    exit(0)

# Unzip the record at the given file and offset.
bytes = []
arcfile = args[0]
offset  = int(args[1])

if offset < 0:
    parser.error('offset cannot be negative: ' + offset)

url=urlsplit( arcfile )
protocol=url[0]

if protocol not in ['', 'file', 'http', 'https' ]:
    print 'Error: unknown protocol:', protocol
    exit(1)

logfile=options.logfile and open(options.logfile, 'ab') or sys.stderr

def log( code, offset, url, *va ):
    print >>logfile, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
    print >>logfile, code,
    print >>logfile, ' ' * (10-len(str(offset))), offset, 
    print >>logfile, url, 
    for s in va:
        print >>logfile, s,
    print >>logfile

def info( message, *va ):
    print >>logfile, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
    print >>logfile, '000'
    print >>logfile, message,
    for s in va:
        print >>logfile, s,
    print >>logfile

def openHttpUrl( url, offset ):
    req = Request( url.geturl() )
    req.add_header( 'Range', 'bytes='+str(offset)+'-' )
    f = urlopen( req )
    return f

def openFileUrl( url, offset ):
    f = open( unquote_plus( url[2] ), 'rb' )
    f.seek( offset )
    return f              

def openFile( url, offset ):
    f = open( url[2], 'rb' )
    f.seek( offset )
    return f

try:
    openers = { '': openFile,
                'file': openFileUrl,
                'http': openHttpUrl,
                'https': openHttpUrl }

    file=None
    try:
        file=openers[protocol]( url, offset )
        bytes = gunzip( file )
    finally:
        file.close()

    arc = ArcRecord( bytes )

    if not isinstance( arc.payload, HttpResponse ):
        raise Exception, 'ArcRecord is not an HTTP response'

    html=Html( arc.payload.body, arc.payload.charset )

    if not html.doc or html.doc.getroot() is None:
        raise Exception, 'Error parsing HTML'

    root=html.doc.getroot()

    xml = DefaultTransformer( html ).transform( )

    print etree.tostring( xml, method='xml', encoding=unicode ).encode('utf-8')

except Exception, message:
    log( '500', offset, url.geturl(), message )
    raise
else:
    log( '200', offset, url.geturl() )
