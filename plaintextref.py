#! /usr/bin/env python3
# -*- coding: utf-8 -*-

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
# - account for multiple occurences of links? (list only once in appendix)
#   > switch references and counter in dictionary
# - allow flags/options for running the script, e.g.
#   + html: define at which tag or words to start scanning the file
#   + html: conversion to text-only but w/o filtering out references yet

import sys
import os
import re
import argparse
from urllib.parse import urlparse
from collections import OrderedDict
from html.parser import HTMLParser
import html.entities

class HTMLClean(HTMLParser):
    """Class to clean HTML tags
    and entities, including script tags.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
        self.urls = []

    def handle_starttag(self, tag, attrs):
        """Look for hyperlinks and filter out their href attribute.
        """
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    the_url = attr[1].strip()
                    if the_url:
                        self.urls.append(the_url)
                        self.result.append(the_url)

    def handle_data(self, data):
        """Add content enclosed within various HTML tags.
        """
        # strip whitespace produced by html indentation
        data = re.sub('( +\n +)', ' ', data)
        data = re.sub('(\n +)', '\n', data)
        self.result.append(data)

    def handle_entityref(self, name):
        """Convert HTML entities to their Unicode representations.
        """
        html_entities = html.entities.name2codepoint[name]
        self.result.append(chr(html_entities))

    def handle_endtag(self, tag):
        """Look for hyperlinks whose <a></a> tags include a description,
        then switch URL and description (as saved in the results list).
        Remove hyperlinks whose <a></a> tags surround other content.
        """
        count_data = len(self.result)
        if tag == "a" and count_data >= 2:
            descriptions = []
            urls_copy = self.urls.copy()
            # remove hyperlink descriptions before closing </a> tags
            # if they do not belong to proper hyperlinks
            # + join hyperlink descriptions that belong together
            if len(urls_copy) >= 1:
                last_url = urls_copy.pop(-1)
                while True and count_data >= 2:
                    last_data = self.result.pop(-1)
                    count_data -= 1
                    if last_data == last_url:
                        break
                    else:
                        descriptions.append(last_data)
                if len(descriptions) == 0:
                    pass
                else:
                    if len(descriptions) > 1:
                        descriptions.reverse()
                        descriptions_collected = ''.join(descriptions)
                    else:
                        descriptions_collected = descriptions[0]
                    url = urlparse(last_url)
                    if url[0] is not '' and url[1] is not '':
                        self.result.append(descriptions_collected)
                        self.result.append(" (" + last_url + ")")
        # remove any data that was inside <script> or <style> tags
        if (tag == "script" or tag
                == "style") and len(self.result) >= 1:
            script = self.result.pop(-1)
    def concatenate(self):
        """Concatenate all individual pieces of data,
        trim whitespace at beginning and end of file, and
        remove any remaining weird newline formatting.
        """
        fulltext = u''.join(self.result)
        fulltext = fulltext.lstrip()
        fulltext = fulltext.rstrip()
        fulltext = re.sub('(\w)( *)(\n)(\w)', r'\1 \4', fulltext)
        fulltext = re.sub('( *\n\n+ *)', '\n\n', fulltext)
        return fulltext

def html_to_text(html):
    content = HTMLClean()
    content.feed(html)
    return content.concatenate()

def inspectbrackets(matchobj):
    """Further break down the regex matches for brackets and quotes.
    """
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
    else:
        return fullref

def writeappendix():
    """Write an appendix (list of references/footnotes).
    """
    global references
    # separate footnotes with separator. use _ instead of dashes
    # as -- is read as the beginning of a signature by e-mail clients
    fout.write("___\n")
    # write appendix/bibliography to output file
    for no, ref in references.items():
        fout.write("[{}] {}\n" .format(no, ref))


parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description = '''---------------
%(prog)s is a program to change text-based files (like HTML)
to proper plaintext and to convert any references (like URLs or citations)
to sequentially numbered footnotes which are appended to the file.

References used for footnotes are URLs enclosed in round brackets
as well as any other text enclosed in square brackets.
Regular text in round brackets, if not preceded by a URL, is ignored.

See https://github.com/kerstin/plaintextref for a more detailed description.
---------------
''')
parser.add_argument("filename",
    help='''name of the file you want to convert;
supported file types are: .txt, .html/.htm, .md''')
parser.add_argument('-s','--start', dest="startparse",
    help = '''define where to start scanning an html file e.g.
--s \"maincontainer\"
--start \"<body>\"
''')
parser.add_argument('-n','--noref', dest="noref",
    help = '''convert the file to plaintext, but don't create an appendix;
useful if you just want to strip html tags and entities''')
args = parser.parse_args()

# split provided filename into name / extension
filename = args.filename
filename_split = filename.split(".")
filename_base = filename_split[0]
ext = filename_split[1].lower()
# create new filename for plaintext output
filename_out = filename_base + "_plaintext." + ext

# create an ordered dictionary to store all references
# add counter for references
# add counter for e-mail signature
references = OrderedDict()
counter = 0
signature = 0

if __name__ == "__main__":
    # validate file exists
    if os.path.isfile(filename) is True:
        # check for valid file types
        if (ext == "txt" or ext == "html"
                or ext == "htm" or ext == "md"):
            with open(filename, 'r', encoding='utf-8') as f:
                print("------------")
                print("Reading input file...")
                # Markdown still unsupported
                if ext == 'md':
                    print("Sorry, Markdown conversion is not yet supported. ):")
                    sys.exit()
                if ext == 'htm' or ext == 'html':
                    # status message
                    print("Converting HTML to plaintext...")
                    # read in html file as one string
                    # and split at <body> tag if present
                    html_to_str = f.read()
                    body_split = html_to_str.split("<body>")
                    if len(body_split) > 1:
                        html_stripped = html_to_text(body_split[1])
                    else:
                        html_stripped = html_to_text(body_split[0])
                    # create iterable list of lines
                    html_stripped_list = html_stripped.splitlines(True)

                    with open(filename_out, 'w+', encoding='utf-8') as fout:
                        fout.write(html_stripped)
                    # exit program after cleaning up html
                    # before filtering out references
                    # sys.exit()

                with open(filename_out, 'w+', encoding='utf-8') as fout:
                    # status message
                    print("Creating footnotes...")
                    if ext == 'html' or ext == 'htm':
                        source = html_stripped_list
                    else:
                        source = f
                    # iterate over all lines
                    for line in source:
                        # if the current line does not mark an e-mail signature
                        if line != "--\n":
                            # search and substitute lines using regex
                            # find all round and square brackets
                            # find all square brackets within quotes
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
                            # write back all lines (changed or unchanged)
                            fout.write(line_out)
                        # include appendix before e-mail signature
                        # if the current line marks such a signature (--)
                        else:
                            signature = 1
                            if len(references) > 0:
                                writeappendix()
                            fout.write("\n" +line)
                    # include appendix at end if no signature was found
                    if signature == 0 and len(references) > 0:
                        fout.write("\n\n")
                        writeappendix()
                    # status message
                    print("DONE.\n")
                    print("The output file is: {}" .format(fout.name))
        # other file type than .txt was used
        else:
            print("You did not specify a valid file name.\n"
            "Only .txt, .htm/.html and .md files can be converted.")
    # file does not exist
    else:
        print("You did not specify a valid file name.")