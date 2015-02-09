#! /usr/bin/env python3

# TODO
# 
# check file type of file input via cli
# differentiate between:
#   plain text (.txt)
#   HTML (.htm, .html)
#   Markdown (.md)
#
# loop through all lines of the file
# search for occurrences of brackets in each line
# use round brackets only if they contain URLs of any kind (://)
# use all square brackets
#
# remove any whitespace preceding the brackets
# replace each pair of brackets with [i]
# where i is a counter that gets incremented
#
# save contents of brackets in a dictionary (?) 
# with counter variable serving as key
#
# add two new lines at end of file
# and output the dictionary sorted by keys (ascending)
# like so: [key] dictionarycontent
#

import sys
import os
import re
from urllib.parse import urlparse
from collections import OrderedDict
# try:
#     # Python3
#     from urllib.parse import urlparse
# except ImportError:
#     # Python2
#     from urlparse import urlparse

# check file type of file input by user via CLI
# + convert extension to lower case just in case
filename = sys.argv[-1]
filename_base, extension = os.path.splitext(filename)
extension = extension.lower()

# number of first reference
counter = 1
brackets = []
references = OrderedDict()

if extension == ".txt":
    # read in the input file
    f = open(filename, 'r')
    # create new file for plaintext output
    filename_out = filename_base + "_plaintext" + extension
    fout = open(filename_out, 'w')

    # iterate over all lines
    for line in f:
        # search lines using regex
        # find all round and square brackets
        # TODO: find only round brackets containing URLs
        brackets.extend(re.finditer("([ ]*[\(])([^\(\)]*)([\)])"
            "|([ ]*[\[])([^\[\]]*)([\]])", line))

    # inspect all brackets found
    for reference in brackets:
        # inspect references in round brackets
        brackets_round = reference.group(2)
        if brackets_round is not None:
            # make sure content of brackets consists only of URLs
            # check for attribute scheme (URL scheme specifier) at index 0
            url = urlparse(brackets_round)
            if url[0] is not '':
                references[counter] = brackets_round
                counter += 1
        # use all references square brackets
        brackets_square = reference.group(5)
        if brackets_square is not None:
            references[counter] = brackets_square
            counter += 1

    # iterate over all references when done reading all lines
    for no, ref in references.items():
        print("[{}] {}" .format(no, ref)) #debug

    f.close()
    fout.close()
elif extension == (".htm" or ".html"):
    # code for HTML files goes here
    print("html!") #debug only
elif extension == ".md":
    # code for Markdown files goes here
    print("markdown!") #debug only
else:
    print("You did not specify a valid file name.\n"
        "Only .txt, .htm/.html and .md files can be converted.")