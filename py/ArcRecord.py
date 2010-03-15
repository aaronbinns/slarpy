#!/usr/bin/python

import sys
import re
from HttpResponse import HttpResponse

# See: http://www.archive.org/web/researcher/ArcFileFormat.php
class ArcRecord():

    fields  = {}
    payload = None

    def __init__(self, bytes=''):
        # http://www.danieldrezner.com/ 63.247.129.166 20080103193531 text/html 6518
        arcline, sep, payload = bytes.partition('\n')

        keys1 = ['url', 'ip-address', 'date', 'content-type', 'length' ]
        keys2 = ['url', 'ip-address', 'date', 'content-type', 'result-code', 'checksum', 'location', 'offset', 'filename', 'length' ]

        values = arcline.split()
        if len(values) > 5:
            fields = zip( keys2, values )
        else:
            fields = zip( keys1, values )

        self.fields  = dict(fields)
        self.payload = payload

        if 'content-type' in self.fields and self.fields['content-type'] == 'text/html':
            self.payload = HttpResponse( payload )

if __name__ == '__main__':
    # Use stdin if no filename given on command-line
    inFile = sys.stdin
    if len(sys.argv) > 1:
        inFile = open( sys.argv[1],"rb" )

    with inFile as input:
        bytes = input.read()

    arc=ArcRecord(bytes)

    print arc.fields
