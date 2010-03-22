#!/usr/bin/python

import sys
import magic

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '-h':
        print sys.argv[0] + " <file>..."
        exit(0)
        
    m = magic.Magic( True )

    for f in sys.argv[1:]:
        print m.from_file( f )
