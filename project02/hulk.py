#!/usr/bin/env python2.7

import hashlib
import itertools
import random
import string
import getopt
import os
import sys

ALPHABET = string.ascii_lowercase + string.digits
LENGTH = 8
HASHES = 'hashes.txt'
PREFIX = ''

# Utility Functions

def usage(exit_code=0):
    print >>sys.stderr, '''Usage: hulk.py [-a ALPHABET -l LENGTH -s HASHES -p PREFIX]\n\nOptions:

    -a  ALPHABET    Alphabet used for passwords
    -l  LENGTH      Length for passwords
    -s  HASHES      Path to file containing hashes
    -p  PREFIX      Prefix to use for each candidate password\n'''
    sys.exit(exit_code)

def md5sum(s):
	return hashlib.md5(s).hexdigest()


# Main Execution

if __name__ == '__main__':
# Parse command-line arguments
	try:
		options, arguments = getopt.getopt(sys.argv[1:], "a:l:s:p:")
	except getopt.GetoptError as e:
		usage(1)

	for option, value in options:
		if option == "-a":
			ALPHABET = value
		elif option == "-l":
			LENGTH = int(value)
		elif option == "-s":
			HASHES = value
		elif option == "-p":
			PREFIX = value
		else:
			usage(1)
#End
	hashes = set([l.strip() for l in open(HASHES)])
	total = len(ALPHABET) ** LENGTH

	for candidate in itertools.product(ALPHABET, repeat=LENGTH):

		candidate = PREFIX + ''.join(candidate)
		checksum = md5sum(candidate)

		if checksum in hashes:
			print candidate
		

