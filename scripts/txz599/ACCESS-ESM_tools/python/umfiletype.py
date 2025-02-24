import struct

def getumfiletype(f):

    # Work out word length and byte order
    # Read first 16 bytes and try to interpret in various ways

    s = f.read(16)

    # For a UM fieldsfile, first word should be 20 and second 1, 2, or 4
    # For ancillary file first word -32768

    wordsize = None

    for endian in ('=', '>', '<'):
        # Use long long to ensure 64 bit integers
        h = struct.unpack("%s2q" % endian, s)
        if h[0] in [20, -32768] and h[1] in (1, 2, 4):
            wordsize = 8
            break
        h = struct.unpack("%s4i" % endian, s)
        if h[0] in [20, -32768] and h[1] in (1, 2, 4):
            wordsize = 4
            break

    if not wordsize and endian:
        raise Exception("Error - file type not determined")

    if endian == '=':
        return wordsize*8, "native"
    elif endian == '>':
        return wordsize*8, "big"
    elif endian == '<':
        return wordsize*8, "little"
    

if __name__ == '__main__':
    import sys

    f = open(sys.argv[1])
    wordsize, endian = getumfiletype(f)
    print "Filetype", wordsize, endian
