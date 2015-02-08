# plaintextref

A Python3 script that moves references (citations or URLs) contained 
within a piece of plain text, HTML formatted text or Markdown formatted 
text out of said text, numbers them and converts them to 
footnotes for better readability.

##Example

Original text:

<pre>Fans keep arguing over if Thranduil (<a href="http://evankart.deviantart.com/art/Thranduil-419996946">http://evankart.deviantart.com/art/Thranduil-419996946</a>) or Thorin (<a href="http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763">http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763</a>) makes the better [... sassier] king.</pre>

<br>
Resulting text:

<pre>Fans keep arguing over if Thranduil[1] or Thorin[2] makes the better[3] king.<br>
[1] <a href="http://evankart.deviantart.com/art/Thranduil-419996946">http://evankart.deviantart.com/art/Thranduil-419996946</a>
[2] <a href="http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763">http://evankart.deviantart.com/art/Thorin-Oakenshield-420365763</a>
[3] ... sassier</pre>

<br>

The script assumes that
* URLs surrounded by round brackets and
* any other text surrounded by square brackets
signify references that are to be turned into footnotes. Regular text surrounded by round brackets is left untouched.

<br>
<hr>

This program, while mostly different in functionality, was in part motivated by [miniref](https://github.com/Lotterleben/miniref).