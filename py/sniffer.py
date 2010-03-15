#!/usr/bin/python

import sys

# Byte sequences to detect encoding via BOM or <?xml> declaration.
# See: http://www.w3.org/TR/xml/#sec-guessing-no-ext-info
BOMS = { '\xef\xbb\xbf'    : 'utf-8',
        '\xfe\xff'         : 'utf-16be',
        '\xff\xfe'         : 'utf-16le',
        '\x00\x00\xFE\xFF' : 'ucs-4be',
        '\xFF\xFE\x00\x00' : 'ucs-4le',
        '\x00\x00\xFF\xFE' : 'ucs-4-a',
        '\xFE\xFF\x00\x00' : 'ucs-4-b'
        }
        
XML_HEADERS = { '\x3C\x3F\x78\x6D' : 'utf-8',  
                '\x00\x3C\x00\x3F' : 'utf-16be',
                '\x3C\x00\x3F\x00' : 'utf-16le',
                '\x3C\x00\x00\x00' : 'ucs-4be',
                '\x00\x3C\x00\x00' : 'ucs-4le',
                '\x00\x00\x3C\x00' : 'ucs-4-3',
                '\x00\x00\x00\x3C' : 'ucs-4-4',
                '\x4C\x6F\xA7\x94' : 'ebcdic'  
                }

def sniffBom( bytes ):
    for k in BOMS:
        if bytes.startswith( k ):
            return BOMS[k]

def sniffXml( bytes ):
    for k in XML_HEADERS:
        if bytes.startswith( k ):
            return XML_HEADERS[k]

def sniffEncoding( bytes ):
    for k in BOMS:
        if bytes.startswith( k ):
            return [ BOMS[k], 'bom' ]
    for k in XML_HEADERS:
        if bytes.startswith( k ):
            return [ XML_HEADERS[k], 'xml' ]
    return [None,None]

if __name__ == '__main__':
    # Use stdin if no filename given on command-line
    inFile = sys.stdin
    if len(sys.argv) > 1:
        inFile = open( sys.argv[1],"rb" )
        
    with inFile as input:
        bytes = input.read( )

    print sniffEncoding( bytes )
