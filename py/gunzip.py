#!/usr/bin/python

import sys
import zlib

# This is taken from the standard Python gzip library code.  The
# Python stdlib does the same as command-line gzip: it unzips the
# whole stream.  But we only want the single record, so we stop after
# the first record is uncompressed.
def gunzip( stream ):
    buf = ""

    FTEXT, FHCRC, FEXTRA, FNAME, FCOMMENT = 1, 2, 4, 8, 16
    
    magic = stream.read(2)
    if magic != '\037\213':
        raise IOError, 'Not a gzipped file'
    method = ord( stream.read(1) )
    if method != 8:
        raise IOError, 'Unknown compression method'
    flag = ord( stream.read(1) )
    # modtime = stream.read(4)
    # extraflag = stream.read(1)
    # os = stream.read(1)
    stream.read(6)

    if flag & FEXTRA:
        # Read & discard the extra field, if present
        xlen = ord(stream.read(1))
        xlen = xlen + 256*ord(stream.read(1))
        stream.read(xlen)

    if flag & FNAME:
        # Read and discard a null-terminated string containing the filename
        while True:
            s = stream.read(1)
            if not s or s=='\000':
                break

    if flag & FCOMMENT:
        # Read and discard a null-terminated string containing a comment
        while True:
            s = stream.read(1)
            if not s or s=='\000':
                break

    if flag & FHCRC:
        stream.read(2)     # Read & discard the 16-bit header CRC

    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    while 1:
        b=stream.read(1024)
        if b=="":
            buf = buf + decompress.flush()
            break
        d=decompress.decompress(b)
        buf = buf + d
        if decompress.unused_data != "":
            break

    return buf

if __name__ == '__main__':
    # Use stdin if no filename given on command-line
    inFile = sys.stdin
    if len(sys.argv) > 1:
        inFile = open( sys.argv[1],"rb" )
        
    with inFile as input:
        input.seek( int( sys.argv[2] ) )
        print gunzip( input ),
