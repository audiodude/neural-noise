# Corpus
Although some effort was made to make these scripts flexible, it should be known
that the original repository that these scripts operated on had an `xml`
directory with a `raw` directory under it. Thus a typical file would be found at
`xml/raw/3d3a9d3ad4ac31903270553ff6b940dcc499c91d`.

The XML files that the `converter.py` script operated on followed the format of
what is found in the samples directory.

## Fixing invalid XML
A large number of the original input source files had percent signs in them, in
the XML tag names. This is illegal XML. The `fix_invalid_xml.sh` shell script
simply runs a find command over the given directory and uses sed to replace
'%20' with '_' globally in all files, editing them in place. It also replaces
tags that start with numbers with an '_' in place of the number.

## Echonest check
The original raw corpus contained several "amateur" songs and other undesirable
pieces. The script `check_echonest.py` is provided for filtering these songs
out. It works by processing a single file at a time, parsing out the artist and
title names. If it can find a fuzzy match for these in the echo nest catalog,
the song passes the filter and its source file is copied to an `xml/existing`
directory. If the song doesn't pass the check, a dummy empty file is placed in
the `xml/nonexistant` directory. This is to speed up subsequent passes of the
script in case it has to be stopped because of an error (see "Fixing invalid
XML"