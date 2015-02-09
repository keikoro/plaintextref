#! /usr/bin/env python3

# Convert in-text references (URLs) to sequentially numbered footnotes.
#
# Copyright (c) 2015 K Kollmann <code∆k.kollmann·moe>
# License: http://opensource.org/licenses/MIT The MIT License (MIT)
#
# You need to have Python 3.x installed to run this script.
# Run by opening the file containing the text you wish to convert.
# The output gets saved to a new file whose name has _plaintext
# appended to the original filename.
# e.g.
# $ python3 plaintextref.py myfile.txt
# results in:
# myfile_plaintext.txt
#
# The script currently only supports conversion of .txt files.
# Round brackets containing URLs and all square brackets get converted
# to footnotes. Round brackets containing other text (including nested
# brackets, round or square) are ignored.

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
    fout.write("\n\n___\n")
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