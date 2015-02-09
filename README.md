# plaintextref

A Python3 program which converts in-text references (citations, URLs) in 
.txt files to sequentially numbered footnotes for better readability.


## Example

Original text:

<pre>Fans keep arguing over if Thranduil (<a href="http://evankart.deviantart.com/art/Thranduil-419996946">http://evankart.deviantart.com/art/Thranduil-419996946</a>) or Thorin (<a href="http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763">http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763</a>) makes the better [... sassier] king.</pre>
<br />
Resulting text:

<pre>Fans keep arguing over if Thranduil[1] or Thorin[2] makes the better[3] king.<br>
[1] <a href="http://evankart.deviantart.com/art/Thranduil-419996946">http://evankart.deviantart.com/art/Thranduil-419996946</a>
[2] <a href="http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763">http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763</a>
[3] ... sassier</pre>
<br />See also sample files [thth.txt](thth.txt) and [thth_plaintext.txt](thth_plaintext.txt)


## Description

This program is particularly useful for making texts like e-mails containing a high number of references (like links to websites) better legible by moving all references out of the running text and into an appendix at the end of the document.

At the same time, the user writing such texts is not required to change their writing habits too much: URLs are put into (regular, round) brackets like they usually might, asides which are better left in the running text can also be kept in round brackets, only citations that should explicitely be converted to footnotes need to be enclosed in square brackets (which are normally lesser-used punctuation marks).

Another intended purpose of this program is the conversion of HTML-formatted e-mails or texts to plain text for better sharing via mailing lists which only support or prefer the sending of plain text e-mails. However, **conversion of HTML documents is currently *not yet* supported**, see **Caveats** below.


## Usage

Start the script by specifying which file you want to convert. The converted text is saved to a new file which has ```_plaintextref``` appended to the original file name. Save location is the folder containing the original file.

```$ python3 plaintextref.py myfile.txt```

... results in a new file called ```myfile_plaintext.txt```


##Caveats

The program assumes that
* URLs surrounded by round brackets and
* any other text surrounded by square brackets
<br>
signify references that are to be turned into footnotes.

Other text surrounded by round brackets (including nested brackets, round or square) is left untouched.

###Needs fixing
Ignore square brackets which are part of citations, used to modify the original quote (to clarify, for translations, to indicate a change in capitalisation etc.) as well as square brackets denoting errors (starting with *sic*).

<br>

The script currently only supports the conversion of **text files**. Adding support for **HTML** and **Markdown files** will be the next steps.

<br>
<hr>

This program, while mostly different in functionality, was in part motivated by [miniref](https://github.com/Lotterleben/miniref).