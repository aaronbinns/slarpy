#!/usr/bin/python

import sys
import re
from HttpResponse import HttpResponse

class WarcRecord():

    version = None
    headers = {}
    block   = ''

    def __init__(self, bytes=''):
        if 'WARC/' == bytes[0:5]:
            self.parseWarc(bytes)
        else:
            # Try Arc
            self.parseArc(bytes)

        # If an HTTP response, parse it too.
        if self.headers['Content-Type'] == 'application/http; msgtype=response':
            self.block = HttpResponse( self.block )


    def parseWarc(self, bytes=''):
        # Note: Since WARC header format is modeled after HTTP
        #       headers, the code to parse them is nearly the same as
        #       in HttpResponse.py.
        
        # Split the headers and the block, which are delineated by a '\r\n\r\n' sequence.
        match = re.search( '\r\n\r\n', bytes, re.MULTILINE );
        headerbytes  = bytes[:match.start()]
        self.block = bytes[match.end():]

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
                self.headers[key] = value
            #else:
            #    current = self.headers[key]
            #    current.append( value )

    # See: http://www.archive.org/web/researcher/ArcFileFormat.php
    def parseArc(self, bytes=''):
        arcline, sep, self.block = bytes.partition('\n')

        keys1 = ['url', 'ip-address', 'date', 'content-type', 'length' ]
        keys2 = ['url', 'ip-address', 'date', 'content-type', 'result-code', 'checksum', 'location', 'offset', 'filename', 'length' ]

        values = arcline.split()
        if len(values) > 5:
            headers = zip( keys2, values )
        else:
            headers = zip( keys1, values )

        headers  = dict(headers)

        self.headers['WARC-Type'] = 'response'
        self.headers['WARC-Target-URI'] = headers['url']
        self.headers['WARC-IP-Address'] = headers['ip-address']
        d = headers['date']
        self.headers['WARC-Date'] = d[0:4]+'-'+d[4:6]+'-'+d[6:8]+'T'+d[8:10]+':'+d[10:12]+':'+d[12:14]+'Z'
        self.headers['Content-Length'] = headers['length']

        # Map schemes to WARC record Content-Type
        schemes = { 
            'http'    : 'application/http; msgtype=response',
            'https'   : 'application/http; msgtype=response',
            'filedesc': 'application/warc-fields',
            'dns'     : 'text/dns',
            }
        
        match = re.match( '([A-Za-z]+):', headers['url'] )
        if match:
            scheme = match.groups()
            self.headers['Content-Type'] = schemes.get( scheme, 'application/octet-stream' )

        # How can we convert to payload digest if we don't know the format of the ARC checksum?
        #self.headers['WARC-Payload-Digest'] = headers['checksum']
        

if __name__ == '__main__':
    inFile = sys.stdin
    if len(sys.argv) > 1:
        inFile = open( sys.argv[1],"rb" )

    with inFile as input:
        bytes = input.read()

    warc=WarcRecord(bytes)

    print warc.headers
    print warc.block
