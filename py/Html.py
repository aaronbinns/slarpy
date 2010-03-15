#!/usr/bin/python

import sys
import re
import sniffer
import unicodedata
import superdec
import HttpResponse
from lxml import etree
from StringIO import StringIO

class Encoding():
    source   = None
    name     = None
    result   = None

    def __init__(self, source=None, name=None, result=None):
        self.source=source
        self.name=name
        self.result=result

    def __str__(self):
        return ",".join( [ 'source='+str(self.source), 
                           'name='+str(self.name), 
                           'result='+str(self.result) ] )
                    
class Html():

    encodings = None
    data      = None
    doc       = None
    metas     = {}

    def __init__(self, bytes='', httpEncoding=None):
        if isinstance(bytes,unicode):
            # TODO: Handle unicode string.
            return

        self.encodings = _buildEncodings( httpEncoding, bytes )

        self.data = _decode(bytes, self.encodings)
        self.data = _stripHeader(self.data)
        self.doc = _parse( self.data )

        if not self.doc or self.doc.getroot() is None:
            return 
        
        meta = Encoding( 'meta', _getMetaCharset( self.doc ) )

        # Possibly re-decode and parse using meta value.
        if all( map( lambda e: not e.result, self.encodings ) ):
            redata = _decode( bytes, [ meta ], fallback=False )
            if meta.result:
                self.data  = redata
                self.doc = _parse( self.data )

        self.encodings.append( meta )

        self.metas = _processMetaTags( self.doc )

def _parse( data ):
    try:
        return etree.parse( StringIO(data), etree.HTMLParser( ) )
    except:
        return None

# Utility to build list of Encodings
def _buildEncodings( httpEncoding, bytes ):
    return [ Encoding('http', httpEncoding ),
             Encoding('bom' , sniffer.sniffBom( bytes ) ),
             Encoding('xml' , sniffer.sniffXml( bytes ) ),
             ]    

# Utility decode given the list of Encodings
def _decode(bytes, encodings, fallback=True):
    doc=None
    for e in encodings:
        if e.name and not superdec.handles( e.name ):
            try:
                doc=bytes.decode(e.name)
                e.result=True
                break
            except:
                e.result=False

    if not doc:
        if not fallback:
            return doc
        else:
            doc=superdec.decode( bytes )
        
    doc = unicodedata.normalize( 'NFKC', doc )

    return doc

# Utility to strip any BOM or <?xml> delcaration off the front.
def _stripHeader( doc ):
    match = re.match( u'\ufeff?(?:[ \t\n\r\f\v]*<[?]xml.+?>)?', doc, re.DOTALL )
    if match:
        doc=doc[match.end():]
    return doc

# Utility to get the first <meta> tag with a valid 'charset=foo' value
def _getMetaCharset( root ):
    charsets = filter( lambda x: x, 
                       map( lambda t: HttpResponse.parseContentType( t.get('content').lower() )[1],
                            root.xpath( "/html/head/meta[@http-equiv and @content]" ) ) )
    return charsets and charsets[0] or None

def _processMetaTags( root ):
    paths = { 'title'      : '/html/head/title/text()',
              'keywords'   : '/html/head/meta[@name="keywords"]/@content',
              'description': '/html/head/meta[@name="description"]/@content',
              'language'   : '/html/head/meta[@name="language"]/@content' }
    metas = { }
    for name, path in paths.items():
        for v in root.xpath( path ):
            if name not in metas:
                metas[name]=[v]
            else:
                metas[name].append(v)

    return metas
        
if __name__ == '__main__':
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

    print html.metas

    for e in html.encodings: 
        print e
    print repr( html.data )
    
    print etree.tostring( html.doc, pretty_print=False, method="xml", encoding=unicode ).encode('utf-8')
