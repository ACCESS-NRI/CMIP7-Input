import os, sys, getopt
import umfiletype

# Usage is subset_um [options] input_file output_file

# Skip the -b -l -n -s options

def usage():
    print "\nsubset_um is a wrapper for Alan Iwi's subset_um utilities that works out"
    print "the correct values for the wordsize and endianness options."
    print "The -b, -l, -n and -s options are not necessry and are not allowed.\n"
    os.system('subset_um_64 -h')
    
try:
    optlist, args = getopt.getopt(sys.argv[1:], 'IPAS:cvh')
except getopt.error:
    print "Usage: getopt error"
    usage()
    sys.exit(2)

fin = open(args[0])
wordsize, endian = umfiletype.getumfiletype(fin)

endianopts = {'big':'-b', 'little':'-l', 'native':'-n'}

prog = "./subset_um_%d" % wordsize
cmd = "%s %s %s" % (prog, endianopts[endian], " ".join(sys.argv[1:]))

print cmd

os.system(cmd)
