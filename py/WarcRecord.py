#!/usr/bin/python

import sys
import re
from HttpResponse import HttpResponse

# See: http://www.archive.org/web/researcher/ArcFileFormat.php
class WarcRecord():

    version = None
    headers = {}
    body    = ''

    def __init__(self, bytes=''):
        # Note: The following bits processing the header lines is
        #       nearly the same as in HttpResponse.py for HTTP header
        #       lines.
        
        # Split the headers and the body, which are delineated by a '\r\n\r\n' sequence.
        match = re.search( '\r\n\r\n', bytes, re.MULTILINE );
        headerbytes = bytes[:match.start()]
        self.body   = bytes[match.end():]

        # Now, fold/combine continuation lines
        r = re.compile ('\n[ \t]+', re.MULTILINE )
        headerbytes = r.sub( ' ', headerbytes )

        headers = headerbytes.splitlines() 
        self.version = headers[0]
        if not re.match( 'WARC[/][0-9]+[.][0-9]+$', self.version ):
            raise Exception, 'Invalid WARC version line: ' + version
        
        # Now process the headers
        for h in headers[1:]:
            match = re.match( '(.+?)[ \t]*:[ \t]*(.+)', h )
            if not match:
                continue
            key, value = match.groups()
            if key not in self.headers:
                self.headers[key] = [ value ]
            else:
                current = self.headers[key]
                current.append( value )

if __name__ == '__main__':
    inFile = sys.stdin
    if len(sys.argv) > 1:
        inFile = open( sys.argv[1],"rb" )

    with inFile as input:
        bytes = input.read()

    warc=WarcRecord(bytes)

    print warc.headers
