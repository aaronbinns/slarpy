#!/usr/bin/python

import codecs
import sys

def fixup(exc):
    if not isinstance(exc, UnicodeDecodeError):
        raise TypeError("don't know how to handle %r" % exc)
    u = u""
    for c in exc.object[exc.start:exc.end]:
        u += unicode(c,"windows-1252", 'ignore')
    return (u, exc.end)

codecs.register_error( 'superdecFixup', fixup )

def decode( bytes ):
    return codecs.getreader( 'utf-8' ).decode( bytes, 'superdecFixup' )[0]

# List of canonical names of the codecs we handle
_codecs = map( lambda c: codecs.lookup( c ).name, 
               ['utf-8', 'iso-8859-1', 'windows-1252', 'us-ascii'] )

def handles( name ):
    try:
        return codecs.lookup( name ).name in _codecs
    except LookupError:
        return False

if __name__ == '__main__':
    # Use stdin if no filename given on command-line
    inFile = sys.stdin
    if len(sys.argv) > 1:
        inFile = open( sys.argv[1],"rb" )

    with inFile as input:
        bytes = input.read()

    u = decode( bytes )

    # We must encode the unicode string back to bytes when writing to the
    # terminal, otherwise Python will use the system default encoding,
    # which could be us-ascii, etc.
    print u.encode('utf-8')
