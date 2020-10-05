# LFencedCodeExtension: a Python Markdown extension
#
# This extension is a modification of the standard FencedCodeExtension
# in the Markdown package. It looks for code passages formatted like
#
# ```
# code
# ```
#
# ~~~
# code
# ~~~
#
# It differs from FencedCodeExtension in these ways:
#
# - You can specify a class for the outer <pre> tag (as distinct from
# the inner <code> tag). Use the keyword argument preclass=VAL.
# - If you also provide preclass2=VAL2, this applies to ~~~ blocks
# (as distinct from ``` blocks).
# - Code highlighting is not supported.
#
# License: [BSD](http://www.opensource.org/licenses/bsd-license.php)
# Extension is copyright 2020 by Andrew Plotkin
# Base Markdown package: https://github.com/Python-Markdown/markdown


from __future__ import unicode_literals
import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class LFencedCodeExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {
            'preclass': [ '', 'Class for the <pre> tag.' ],
            'preclass2': [ '', 'Class for the <pre> tag (~~~ blocks).' ]
        }
        super(LFencedCodeExtension, self).__init__(**kwargs)

    def extendMarkdown(self, md):
        """ Add LFencedBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        md.preprocessors.register(LFencedBlockPreprocessor(md, self.getConfigs()), 'lfenced_code_block', 25)


class LFencedBlockPreprocessor(Preprocessor):
    FENCED_BLOCK_RE = re.compile(r'''
(?P<fence>^(?:~{3,}|`{3,}))[ ]*         # Opening ``` or ~~~
(\{?\.?(?P<lang>[\w#.+-]*))?[ ]*        # Optional {, and lang
# Optional highlight lines, single- or double-quote-delimited
(hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*
}?[ ]*\n                                # Optional closing }
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)
    CODE_WRAP = '<pre%s><code%s>%s</code></pre>'
    LANG_TAG = ' class="%s"'

    def __init__(self, md, config):
        super(LFencedBlockPreprocessor, self).__init__(md)

        self.preclass = config['preclass']
        self.preclass2 = config.get('preclass2', self.preclass)

    def run(self, lines):
        """ Match and store LFenced Code Blocks in the HtmlStash. """

        text = "\n".join(lines)
        while 1:
            m = self.FENCED_BLOCK_RE.search(text)
            if m:
                delim = m.group('fence')[0]
                preclass = self.preclass
                if delim == '~':
                    preclass = self.preclass2
                if preclass:
                    preclass = self.LANG_TAG % preclass
                    
                lang = ''
                if m.group('lang'):
                    lang = self.LANG_TAG % m.group('lang')

                code = self.CODE_WRAP % (preclass,
                                         lang,
                                         self._escape(m.group('code')))

                placeholder = self.md.htmlStash.store(code)
                text = '%s\n%s\n%s' % (text[:m.start()],
                                       placeholder,
                                       text[m.end():])
            else:
                break
        return text.split("\n")

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def makeExtension(**kwargs):  # pragma: no cover
    return LFencedCodeExtension(**kwargs)
