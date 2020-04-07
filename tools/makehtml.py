#!/usr/bin/env python3

# This fussy little script converts Markdown to HTML. It includes
# some custom extensions which allow the Markdown spec files to be
# tidier while still generating the formatting we want.

import sys
import re
import markdown

from numberingtoc import NumberingTocExtension
from lfencecode import LFencedCodeExtension
from comment import CommentExtension

if len(sys.argv) <= 2:
    print('usage: build.py infile.md template.html outfile.html')
    sys.exit(-1)
    
infilename = sys.argv[1]
templatename = sys.argv[2]
outfilename = sys.argv[3]

infl = open(infilename, encoding='utf-8')
source = infl.read()
infl.close()

infl = open(templatename, encoding='utf-8')
template = infl.read()
infl.close()

# Extract the document title (assumed to be the first text line).
match = re.search('\\s*#([^{]+){', source, re.M)
title = match.group(1).strip()

# Convert Markdown to HTML.
# The NumberingTocExtension arguments are slightly different for the Glulx Technical reference; its headers aren't the same depth as the other files.
if 'Technical' in title:
    number_top_start = 1
    toc_depth = '3-5'
else:
    number_top_start = 0
    toc_depth = '2-5'

# Do the Markdown conversion.
converter = markdown.Markdown(extensions=[
    'attr_list',
    LFencedCodeExtension(preclass='DefFun'),
    NumberingTocExtension(number_top_start=number_top_start, baselevel=1, toc_depth=toc_depth),
    CommentExtension()
])
result = converter.convert(source)

# Shove the result into our template.

header, dummy, footer = template.partition('$BODY$')
header = header.replace('$TITLE$', title)

# Write out the result. We specify ASCII encoding (all Unicode characters
# escaped).

outfl = open(outfilename, 'w', encoding='ascii', errors='xmlcharrefreplace')
outfl.write(header)
outfl.write(result)
outfl.write(footer)
outfl.close()

