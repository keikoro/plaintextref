#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Convert in-text references (URLs) to sequentially numbered footnotes and
# change text-based files (like HTML) to proper plaintext in the process.
#
# Copyright (c) 2015 K Kollmann <code∆k.kollmann·moe>
# License: http://opensource.org/licenses/MIT The MIT License (MIT)

# You need to have Python 3.x installed to run this script.
# Use -h or --help for help on how to use the program.
#
# The script currently supports conversion of .txt and .html/.htm files.
# Round brackets containing URLs and square brackets get converted
# to footnotes. Round brackets containing other text (including any nested
# brackets) and square brackets within quotes to denote changes to
# original citations as well as [sic] and [sic!] are ignored.
#
# TODO:
# - ignore or warn on square brackets containing only digits
#   as these might already be footnotes
#   (possibly then check for appendix, integrate existing footnotes via cli option)
# - option to re-index an existing appendix / to combine old and new refs

# Python2
from __future__ import unicode_literals
import copy
# Python3 + Python2
import sys
import os
import re
import argparse
import errno
from collections import OrderedDict

try:
    # Python2
    from io import open
except ImportError:
    pass
try:
    from urllib.parse import urlparse
# Python2
except ImportError:
    from urlparse import urlparse
try:
    from html.parser import HTMLParser
# Python2
except ImportError:
    from HTMLParser import HTMLParser
try:
    import html.entities
# Python2
except ImportError:
    import htmlentitydefs


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
        if tag == "br":
            self.result.append('\n')
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
        # data = re.sub('( +\n +)', ' ', data)
        # data = re.sub('(\n +)', '\n', data)
        data = data.lstrip()
        self.result.append(data)

    def handle_entityref(self, name):
        """Convert HTML entities to their Unicode representations.
        """
        try:
            html_entities = html.entities.name2codepoint[name]
            self.result.append(chr(html_entities))
        # Python2
        except:
            html_entities = htmlentitydefs.name2codepoint[name]
            self.result.append(unichr(html_entities))

    def handle_endtag(self, tag):
        """Look for hyperlinks whose <a></a> tags include a description,
        then switch URL and description (as saved in the results list).
        Remove hyperlinks whose <a></a> tags surround other content.
        """
        count_data = len(self.result)
        # linebreaks, paragraphs
        if tag == "div":
            self.result.append('\n\n')
        if tag == "p":
            self.result.append('\n\n')
        # URL handling
        if tag == "a" and count_data >= 2:
            descriptions = []
            try:
                urls_copy = self.urls.copy()
            except:
                urls_copy = copy.copy(self.urls)
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
                    if url.scheme != '' and url.netloc != '':
                        self.result.append(descriptions_collected)
                        self.result.append(" (" + last_url + ")")
        # remove any data that was inside <script> or <style> tags
        if (tag == "script" or tag
                == "style") and len(self.result) >= 1:
            script = self.result.pop(-1)
    def concatenate(self):
        """Concatenate all individual pieces of data,
        trim whitespace at beginning and end of file and
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

def inspect_brackets(matchobj):
    """Further break down the regex matches for brackets and quotes.
    """
    global counter
    global references
    fullref = matchobj.group(0)
    brkts_rd_content = matchobj.group('rd')
    brkts_sq_inquote = matchobj.group('sq_qu_reg')
    brkts_sq_inquote_2 = matchobj.group('sq_qu_form')
    brkts_sq_content = matchobj.group('sq')
    # brkts_rd_space = matchobj.group('rd_space')
    # brkts_rd_special = matchobj.group('rd_special')
    # brkts_sq_space = matchobj.group('sq_space')
    # brkts_sq_special = matchobj.group('sq_special')

    # if brkts_rd_space is None and brkts_rd_special is None:
    #     rd_space = " "
    # else:
    #     rd_space = ""
    # if brkts_sq_space is None and brkts_sq_special is None:
    #     sq_space = " "
    # else:
    #     sq_space = ""
    # regex search found round brackets
    if brkts_rd_content is not None:
        # verify brackets start with URL;
        # check for attributes: scheme (URL scheme specifier) and
        # netlocat (Network location part)
        url = urlparse(brkts_rd_content)
        if url.scheme != '' and url.netloc != '':
            if brkts_rd_content in references:
                refno = references[brkts_rd_content]
                # status msg
                print("::: Note: Multiple occurrence of reference {}"
                            .format(brkts_rd_content))
            else:
                counter += 1
                refno = counter
                references[brkts_rd_content] = refno
            ref = "[" + str(refno) + "]"
            return ref
        # return original bracket content if it's not a URL
        else:
            return fullref
    # regex search found square brackets
    elif brkts_sq_inquote is not None or brkts_sq_inquote_2 is not None:
        return fullref
    elif brkts_sq_content is not None:
        if brkts_sq_content != 'sic' and brkts_sq_content != 'sic!':
            if brkts_sq_content in references:
                refno = references[brkts_sq_content]
                # status msg
                print("::: Note: Multiple occurrence of reference "
                        "\"{}\"".format(brkts_sq_content))
            else:
                counter += 1
                refno = counter
                references[brkts_sq_content] = refno
            ref = "[" + str(refno) + "]"
            return ref
        else:
            return fullref
    # regex search did not find any brackets in this line
    else:
        return fullref

def write_appendix():
    """Write an appendix (list of references/footnotes).
    """
    # separate footnotes with separator. use _ instead of dashes
    # as -- is read as the beginning of a signature by e-mail clients
    try:
        fout.write('___\n')
    except TypeError:
        fout.write(u'___\n')
    # write appendix/bibliography to output file
    for ref, no in references.items():
        try:
            fout.write("[{}] {}\n" .format(no, ref))
        except TypeError:
            fout.write(u"[{}] {}\n" .format(no, ref))

def newfilepath(**allpaths):
    """Check writability of the path provided for the output file.
    """
    for key in allpaths:
        # append missing / to paths
        try:
            if allpaths[key] is not "" and allpaths[key][-1:] is not '/':
                allpaths[key] += '/'
        except:
            allpaths[key] = ''
        # replace leading ~ with HOME dir in paths input as string
        if allpaths[key].find("~") != -1:
            allpaths[key] = os.path.expanduser(allpaths[key])
    try:
        oldpath = allpaths['oldpath']
        argpath = allpaths['argpath']
        cwd = allpaths['cwd']
    except:
        sys.exit("Argument missing. Please check your program code.")

    if argpath is not '':
        newpath = ""
    else:
        newpath = oldpath

    # check pathnames for writability
    while newpath == "":
        if argpath == oldpath:
            newpath = oldpath
            continue # continue at else statement in while-else
        else:
            if os.access(argpath, os.W_OK) == True:
                newpath = argpath
                break # main program starts running here
            else:
                # status msg
                print("The specified path is not a writable directory.\n"
                    "Trying to save to the directory containing the original file.")
                newpath = oldpath
                continue # continue as else statement in while-else
    else:
        if os.access(newpath, os.W_OK) == True:
            pass # main program starts running here
        else:
            if newpath == cwd:
                # error/exit msg
                sys.exit("The directory containing the original file/\n"
                            "the current working directory is not writable.\n"
                            "Exiting.")
            else:
                # status msg
                print("The directory containing the original file is not writable.")
                if argpath == oldpath or argpath == cwd:
                    sys.exit("Exiting.")
                else:
                    print("Trying to save to the current working directory.")
                    newpath = cwd
                    if os.access(newpath, os.W_OK) == True:
                        print("writable?")
                        pass # main program starts running here
                    else:
                        sys.exit("The current working directory is not writable.\n"
                                    "Exiting.")
    return newpath

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
    help='''name of (path to) the file you want to convert;
supported file types are: .txt, .html/.htm, .md''')
parser.add_argument('-b','--begin', dest="begin", metavar="\"TEXT\"",
    help = '''define where to begin scanning an HTML file
e.g. --begin \"<body>\",
e.g. --b \"2 February 2015\"''')
parser.add_argument('-c','--contain', dest="contain", action="store_true",
    help = '''run argument -b containg the text provided;
by default, parsing begins only after the given string''')
# parser.add_argument('-i','--images', dest="images", action="store_true",
#     help = '''treat image files in <a></a> tags as part of the link description;
# default is to strip <img> tags from converted HTML files''')
parser.add_argument('-a','--append', dest="suffix", metavar="SUFFIX",
    default="_plaintext",
    help = '''the suffix to append to the filename of the output file;
defaults to _plaintext being added to the original filename''')
parser.add_argument('-s','--save', dest="newname", metavar="FILENAME",
    help = '''the name to save the new file under if you do not want to
simply append a suffix to the original filename (see -a);
the file extension of the original file gets added in any case
''')
parser.add_argument('-p','--path', dest="path",
    help = '''path to save the converted file to if you do not want to
save it in the same directory as the original file
''')
# parser.add_argument('-r','--re-index', dest="reindex", action="store_true",
#     help = '''if there are already footnotes and an appendix present,
# renumber existing references and incorporate them
# into a new appendix including both old and new references''')
parser.add_argument('-n','--noref', dest="noref", action="store_true",
    help = '''convert the file to plaintext, but don't create an appendix;
useful if you just want to strip HTML tags''')
args = parser.parse_args()

# create an ordered dictionary to store all references
# add counter for references
# add counter for e-mail signature
references = OrderedDict()
suffix = "_plaintext"
counter = 0
signature = 0

if __name__ == "__main__":

    fullpath = os.path.realpath(args.filename)
    # validate provided filename
    try:
        f = open(fullpath, 'r')
    except OSError as e:
        # filename is a directory or invalid filename
        if e.errno == errno.EISDIR or e.errno == errno.ENOENT:
            sys.exit("You did not specify a valid file name.")
        # no permission to read the file
        elif e.errno == errno.EACCES:
            sys.exit("The specified file cannot be read from.")
        else:
            print(e)
    else:
        filepath, filename = os.path.split(fullpath)
        f.close()

    newpath = newfilepath(oldpath=filepath, cwd=os.getcwd(), argpath=args.path)

    fileroot, extension = os.path.splitext(filename)
    # check for file root and extension
    if extension is "":
        # status msg
        print("::: Attn: the provided file has no file extension.")
        separator = ""
    else:
        separator = "."
        extsplit = extension.split(separator)
        extension = extsplit[-1]

    #check for new filename and suffix
    if args.suffix is not "":
        suffix = args.suffix
    if args.newname is not None and args.newname is not "":
        fileroot = args.newname
    filename_out = newpath + fileroot + suffix + separator + extension

    # only allow files up to 1MB in size
    if os.path.getsize(fullpath) <= 2000000:
        with open(fullpath, 'r', encoding='utf-8') as f:
            # Markdown still unsupported
            if extension == 'md':
                sys.exit("Sorry, Markdown conversion is not yet supported. ):")
            else:
                print("Reading input file...")
            if extension == 'htm' or extension == 'html':
                # status msg
                print("Converting HTML to plaintext...")
                # read in html file as one string
                # and split at user-provided tag or string if present
                html_string = f.read()
                if args.begin:
                    beginparse = args.begin
                    try:
                        html_split = html_string.split(beginparse, maxsplit=1)
                    except TypeError:
                        html_split = html_string.split(beginparse, 1)
                    if len(html_split) > 1:
                        if args.contain is True:
                            parsestring = beginparse + html_split[1]
                        else:
                            parsestring = html_split[1]
                        html_stripped = html_to_text(parsestring)
                    else:
                        # status msg
                        print("::: Attn: the starting point \"" + beginparse
                            + "\" for parsing was not found.")
                        html_stripped = html_to_text(html_split[0])
                else:
                    html_stripped = html_to_text(html_string)
                # create iterable list of lines
                html_stripped_lines = html_stripped.splitlines(True)
                with open(filename_out, 'w+', encoding='utf-8') as fout:
                    fout.write(html_stripped)
                # don't create any footnotes if --noref flag is set
                # (only converts html to plaintext)
                if args.noref:
                    # status msg
                    print("DONE.")
                    print("The output file is: {}" .format(fout.name))
                    sys.exit()

            with open(filename_out, 'w+', encoding='utf-8') as fout:
                # status msg
                print("Looking for references...")
                if extension == 'html' or extension == 'htm':
                    source = html_stripped_lines
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
                                inspect_brackets, line)
                        # write back all lines (changed or unchanged)
                        fout.write(line_out)
                    # include appendix before e-mail signature
                    # if the current line marks such a signature (--)
                    else:
                        signature = 1
                        if len(references) > 0:
                            write_appendix()
                            # status msg
                            print("Appendix created.")
                        else:
                            # status msg
                            print("No references found.")
                        try:
                            fout.write('\n' +line)
                        except:
                            fout.write(u'\n' +line)
                # include appendix at end if no signature was found
                if signature == 0 and len(references) > 0:
                    try:
                        fout.write('\n\n')
                    except:
                        fout.write(u'\n\n')
                    write_appendix()
                    # status msg
                    print("Appendix created.")
                if len(references) <= 0:
                    # status msg
                    print("No references found.")
                # status msg
                print("DONE.")
                print("The output file is: {}" .format(fout.name))
    else:
        print("File size must be below 2MB.")