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

try:
    # Python3
    from urllib.parse import urlparse
except ImportError:
    # Python2
    from urlparse import urlparse

# check file type of file input by user via cli
# + convert extension to lower case just in case
filename = sys.argv[-1]
filename_base, extension = os.path.splitext(filename)
extension = extension.lower()

# number of first reference
counter = 1

if extension == ".txt":
    # read in the file
    f = open(filename, 'r')

    # iterate over all lines
    for line in f:
        # search lines using regex

        # find all round brackets
        # TODO: find only round brackets containing URLs
        brackets = re.findall("([ ]*[\(])([^\(\)]+)([\)])", line)
        # find all square brackets
        # brackets = re.findall("([ ]*[\[])([^\[\]]+)([\]])", line)

        for reference in brackets:
            print("found {} {}" .format(counter, reference)) #debug
            counter += 1

    f.close()
elif extension == (".htm" or ".html"):
    # code for HTML files goes here
    print("html!") #debug only
elif extension == ".md":
    # code for Markdown files goes here
    print("markdown!") #debug only
else:
    print("You did not specify a valid file name.\n"
        "Only .txt, .htm/.html and .md files can be converted.")