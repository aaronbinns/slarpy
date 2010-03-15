#!/usr/bin/python

import sys
import re

class HttpResponse():

    cruft    = None
    httpline = None
    httpver  = None
    statcode = None
    statmsg  = None
    headers  = {}
    body     = ''
    type     = None
    charset  = None

    def __init__(self, bytes=''):
        # First, find the line starting with 'HTTP/'
        match = re.search( 'HTTP/([0-9]+\.[0-9]+)[ ](.+?)[ ](.+?)\n', bytes )
        if not match:
            return

        self.httpline = bytes[match.start():match.end()-1]
        self.httpver  = match.group(1)
        self.statcode = match.group(2)
        self.statmsg  = match.group(3)
        # If the HTTP status line didn't start at byte 0, remove any
        # cruft in front of it.
        if match.start() > 0:
            self.cruft = bytes[0:match.start()]

        # Chop off the cruft and HTTP status line we just processed
        bytes = bytes[match.end():]

        # Split the headers and body
        match = re.search( '\r?\n\r?\n', bytes , re.MULTILINE )
        if not match:
            return

        headerbytes = bytes[:match.start()]
        self.body   = bytes[match.end():]
        
        # Now, fold/combine continuation lines
        r = re.compile ('\n[ \t]+', re.MULTILINE )
        headerbytes = r.sub( ' ', headerbytes )
        headerbytes = headerbytes.lower()

        # Now process each line
        for h in headerbytes.splitlines():
            match = re.match( '(.+?)[ \t]*:[ \t]*(.+)', h )
            if not match:
                continue
            key, value = match.groups()
            if key not in self.headers:
                self.headers[key] = [ value ]
            else:
                current = self.headers[key]
                current.append( value )

        # Special treatment of Content-Type header
        if 'content-type' in self.headers:
            # We only take the first value, in case there were many
            self.type, self.charset = parseContentType( self.headers['content-type'][0] )

    def getBody(self):
        return self.body;

    def getContentType(self):
        return self.type

    def getCharset(self):
        return self.charset

# Utility function to parse the 'content-type' header values.
# Handles lots of common cases:
#    text/html
#    text/html; charset=utf-8
#    text/html; charset=
#    text/html; charset=utf-8
#    text/html; charset='utf-8'
#    text/html; charset=charset=utf-8
#    text/html;     charset =   "us-ascii
# etc.
_re = '([^; \t]+)[ \t]*[;]?[ \t]*(?:.*?(?:charset[\t ]*=[\t ]*)+["\']?([^"\']+)["\']?)?'
def parseContentType( s ):
    match = re.search( _re, s )
    if match:
        return match.groups()
    return [ None, None ]

if __name__ == '__main__':
    # Use stdin if no filename given on command-line
    inFile = sys.stdin
    if len(sys.argv) > 1:
        inFile = open( sys.argv[1],"rb" )

    with inFile as input:
        bytes = input.read()

    res=HttpResponse( bytes )
    print "raw    :", res.headers['content-type']
    print "Type   :", res.getContentType()
    print "Charset:", res.getCharset()
