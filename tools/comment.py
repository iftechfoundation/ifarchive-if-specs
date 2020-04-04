# CommentExtension: a Python Markdown extension
#
# This extension looks for inline spans of the form
#     [[Text.]]
# and translates them into spans of the form
#     <span class="Comment">Text.</span>
#
# A comment span can include code sections if you write:
#
# [[Here is some code.
#     def foo():
#         pass
# Enjoy.]]
#
# (Unlike true Markdown preformatted sections, these code lines are not
# exempt from Markdown translation. They also may not contain completely
# blank lines.)
#
# License: [BSD](http://www.opensource.org/licenses/bsd-license.php)
# Extension is copyright 2020 by Andrew Plotkin
# Base Markdown package: https://github.com/Python-Markdown/markdown

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree

MYPATTERN = r'\[\[([^]]+)\]\]'

class CommentPattern(InlineProcessor):
    def handleMatch(self, match, data):
        text = match.group(1)
        if '\n' not in text:
            el = etree.Element('span')
            el.attrib['class'] = 'Comment'
            el.text = '[' + text + ']'
            return el, match.start(0), match.end(0)
        
        el = etree.Element('span')
        el.attrib['class'] = 'Comment'
        
        subel = etree.Element('span')
        subel.text = '['
        el.append(subel)

        lines = []
            
        while text:
            pos = text.find('\n')
            if pos < 0:
                lines.append(text)
                text = ''
            else:
                lines.append(text[ : pos+1 ])
                text = text[ pos+1 : ]

        ix = 0
        while ix < len(lines):
            jx = ix
            while lines[jx].startswith('    ') and lines[jx].endswith('\n'):
                jx += 1
            if jx > ix:
                subel = etree.Element('br')
                el.append(subel)
                subel = etree.Element('code')
                subel.attrib['class'] = 'CommentCode'
                subel.text = ''.join(lines[ ix : jx ])
                el.append(subel)
                ix = jx
                continue

            subel = etree.Element('span')
            subel.text = lines[ix]
            el.append(subel)
            ix += 1
                
        subel = etree.Element('span')
        subel.text = ']'
        el.append(subel)
        
        return el, match.start(0), match.end(0)
        

class CommentExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(CommentPattern(MYPATTERN), 'comment', 0)
        
