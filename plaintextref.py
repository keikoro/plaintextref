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

def inspectbrackets(matchobj):
    global counter
    global references
    brkts_rd_o = matchobj.group(1)
    brkts_rd_content = matchobj.group(2)
    brkts_sq_content = matchobj.group(5)
    # regex search found round brackets
    if brkts_rd_content is not None:
        # make sure content of brackets consists only of URLs
        # check for attribute scheme (URL scheme specifier) at index 0
        url = urlparse(brkts_rd_content)
        if url[0] is not '':
            counter += 1
            references[counter] = brkts_rd_content
            ref = "[" + str(counter) + "]"
            return ref
        # return original bracket content if it's not a URL
        else:
            return brkts_rd_o + brkts_rd_content + ")"
    # regex search found square brackets    
    elif brkts_sq_content is not None:
        counter += 1
        ref = "[" + str(counter) + "]"
        references[counter] = brkts_sq_content
        return ref
    # regex search did not find any brackets in this line
    # use None to return the original line
    else:
        return None

# check file type of file input by user via CLI
# + convert extension to lower case just in case
filename = sys.argv[-1]
filename_base, extension = os.path.splitext(filename)
extension = extension.lower()

# number of first reference
counter = 0
# create an order dictionary to store all references
references = OrderedDict()

# code for text files goes here
if extension == ".txt":
    # read in the input file
    f = open(filename, 'r')
    # create new file for plaintext output
    filename_out = filename_base + "_plaintext" + extension
    fout = open(filename_out, 'w')

    # iterate over all lines
    for line in f:
        # search and substitute lines using regex
        # find all round and square brackets
        # check for URLs in round brackets with external function
        line_out = re.sub("([ ]*[\(])([^\(\)]*)([\)])"
            "|([ ]*[\[])([^\[\]]*)([\]])", inspectbrackets, line)

        # write all lines (changed or unchanged) to output file
        fout.write(line_out)
    # separate footnotes from running text with separator
    # use underscores i/st of dashes as -- often signal signatures in e-mails
    fout.write("\n___\n")
    # write references/bibliography to output file
    for no, ref in references.items():
        fout.write("[{}] {}\n" .format(no, ref))

    # close both the input and output file when done
    f.close()
    fout.close()
# code for HTML files goes here
elif extension == (".htm" or ".html"):
    print("html!") #debug only
# code for Markdown files goes here
elif extension == ".md":
    print("markdown!") #debug only
else:
    print("You did not specify a valid file name.\n"
        "Only .txt, .htm/.html and .md files can be converted.")