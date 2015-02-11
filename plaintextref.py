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

# TODO:
# check for existence of marker for e-mail signatures
# (two dashes followed by a newline)
# add appendix before signature

import sys
import os
import re
from urllib.parse import urlparse
from collections import OrderedDict

def inspectbrackets(matchobj):
    global counter
    global references
    fullref = matchobj.group(0)
    brkts_rd_content = matchobj.group('rd')
    brkts_sq_inquote = matchobj.group('sq_qu_reg')
    brkts_sq_inquote_2 = matchobj.group('sq_qu_form')
    brkts_sq_content = matchobj.group('sq')
    # regex search found round brackets
    if brkts_rd_content is not None:
        # make sure content of brackets consists only of URLs
        # check for attribute scheme (URL scheme specifier) at index 0
        url = urlparse(brkts_rd_content)
        if url[0] is not '' and url[1] is not '':
            counter += 1
            references[counter] = brkts_rd_content
            ref = "[" + str(counter) + "]"
            return ref
        # return original bracket content if it's not a URL
        else:
            return fullref
    # regex search found square brackets    
    elif brkts_sq_inquote is not None or brkts_sq_inquote_2 is not None:
        return fullref
    elif brkts_sq_content is not None:
        if brkts_sq_content != 'sic' and brkts_sq_content != 'sic!':
            counter += 1
            ref = "[" + str(counter) + "]"
            references[counter] = brkts_sq_content
            return ref
        else:
            return fullref
    # regex search did not find any brackets in this line
    # use None to return the original line
    else:
        return fullref

def writeappendix():
    global references
    # if there are footnotes: separate them with separator
    # use _ not dashes as -- often signals signatures in e-mails
    if len(references) > 0:
        fout.write("___\n")
        # write references/bibliography to output file
        for no, ref in references.items():
            fout.write("[{}] {}\n" .format(no, ref))

# check file type of file input by user via CLI
# + convert extension to lower case just in case
filename = sys.argv[-1]
filename_base, extension = os.path.splitext(filename)
extension = extension.lower()
# create new file for plaintext output
filename_out = filename_base + "_plaintext" + extension

# number of first reference
counter = 0
# create an order dictionary to store all references
references = OrderedDict()
# counter for signature
signature = 0

# code for text files goes here
if extension == ".txt":
    # read in the input file
    with open(filename, 'r', encoding='utf-8') as f:
        with open(filename_out, 'w', encoding='utf-8') as fout:
            # iterate over all lines
            for line in f:
                # if the current line does not mark an e-mail signature
                if line != "--\n":
                    # search and substitute lines using regex
                    # find all round and square brackets
                    # check bracket contents with external function
                    # TODO check for different (faux) quotation mark characters
                    # see http://unicode.org/cldr/utility/confusables.jsp?a=%22&r=None
                    line_out = re.sub(""
                        "(?#check for round brackets)"
                        "([ ]*[\(])(?P<rd>[^\(\)]*)([\)])"
                        "(?#check for square brackets inside regular quotation marks)"
                        "|([\"][^\"[]*)([\[])(?P<sq_qu_reg>[^\"\]]+)([\]])([^\"]*[\"])"
                        "(?#check for square brackets inside formatted quotation marks)"
                        "|([“][^“”[]*)([\[])(?P<sq_qu_form>[^”\]]+)([\]])([^”]*[”])"
                        "(?#check for square brackets)"
                        "|([ ]*[\[])(?P<sq>[^\[\]]*)([\]])",
                            inspectbrackets, line)
                    # write all lines (changed or unchanged) to output file
                    fout.write(line_out)
                # include the appendix before the signature
                # if the current line marks an e-mail signature (--)
                else:
                    signature = 1
                    if len(references) > 0:
                        writeappendix()
                    fout.write("\n" +line)
            if signature != 1 and len(references) > 0:
                fout.write("\n\n")
                writeappendix()
# code for HTML files goes here
elif extension == (".htm" or ".html"):
    print("html!") #debug only
# code for Markdown files goes here
elif extension == ".md":
    print("markdown!") #debug only
else:
    print("You did not specify a valid file name.\n"
        "Only .txt, .htm/.html and .md files can be converted.")