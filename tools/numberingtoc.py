# NumberingToc: a Python Markdown extension
#
# This extension is an extension (no pun intended) of the standard
# TocExtension in the Markdown package. It looks for header lines
# and assembles a table-of-contents section, which is inserted in
# the document when a [TOC] tag is used.
#
# It adds these features:
#
# - Each header is automatically numbered with hierarchical index
# numbers: 1, 1.1, 1.2, 1.2.1, etc. These indexes are used in both the
# [TOC] and the headers.
# - The first top-level section can start at any number (use the
# keyword argument number_top_start=N).
# - You can adjust the number of a section by adding {: data-tocname="N" }.
# A letter or other string is okay too, but of course then following sections
# can't auto-increment.
# - Internal links of the form "[*](#id)" will be linked with the
# text 'section INDEX, "TITLE"'.
#
# License: [BSD](http://www.opensource.org/licenses/bsd-license.php)
# Additions copyright 2020 by Andrew Plotkin
# Base Markdown package: https://github.com/Python-Markdown/markdown

from markdown.extensions.toc import TocExtension, TocTreeprocessor
from markdown.extensions.toc import Extension, string_type, stashedHTML2text, unique, nest_toc_tokens

class NumberingTocTreeprocessor(TocTreeprocessor):

    def __init__(self, md, config):
        super(NumberingTocTreeprocessor, self).__init__(md, config)

        self.number_top_start = config['number_top_start']
        self.header_link_label = config['header_link_label']

    def replace_section_links(self, el, toc_map):
        if el.tag == 'a' and el.text == '*':
            val = el.attrib['href']
            if val.startswith('#'):
                val = val[1:]
                if val in toc_map:
                    sect, name = toc_map[val]
                    el.text = '%s%s, "%s"' % (self.header_link_label, sect, name,)
        for child in el:
            self.replace_section_links(child, toc_map)
        
    def run(self, doc):
        # Get a list of id attributes
        used_ids = set()
        for el in doc.iter():
            if "id" in el.attrib:
                used_ids.add(el.attrib["id"])

        numbering = []
        toc_map = {}
        
        toc_tokens = []
        for el in doc.iter():
            if isinstance(el.tag, string_type) and self.header_rgx.match(el.tag):
                self.set_level(el)
                if int(el.tag[-1]) < self.toc_top or int(el.tag[-1]) > self.toc_bottom:
                    continue
                text = ''.join(el.itertext()).strip()

                # Do not override pre-existing ids
                if "id" not in el.attrib:
                    innertext = stashedHTML2text(text, self.md)
                    # Escaping isn't quite right for `<foo>` in headers; fix it.
                    innertext = innertext.replace('&lt;', '<')
                    innertext = innertext.replace('&gt;', '>')
                    el.attrib["id"] = unique(self.slugify(innertext, self.sep), used_ids)

                depth = int(el.tag[-1]) - self.toc_top + 1
                if len(numbering) > depth:
                    del numbering[ depth : ]
                if len(numbering) < depth:
                    while len(numbering) < depth:
                        firstval = 1
                        if depth == 1:
                            firstval = self.number_top_start
                        numbering.append(firstval)
                else:
                    numval = el.attrib.get('data-tocname')
                    if not numval:
                        # This might be a number or a letter, but let's try to handle it as a number if possible. Makes for better incrementing later.
                        numval = numbering[depth-1] + 1
                        try:
                            numval = int(numval)
                        except:
                            pass
                    numbering[depth-1] = numval

                indexstr = '.'.join([ str(val) for val in numbering ])
                namestr = el.attrib.get('data-toc-label', text)
                toc_map[el.attrib["id"]] = ( indexstr, namestr )
                
                toc_tokens.append({
                    'level': int(el.tag[-1]),
                    'id': el.attrib["id"],
                    'name': indexstr + '. ' + namestr
                })

                # If a tag looks like "## `<foo>`", then there may be no text.
                # (We'll still generate the subtag.)
                eltext = el.text if el.text else ''
                el.text = indexstr + '. ' + eltext
                
                # Remove the data-toc-label attribute as it is no longer needed
                if 'data-toc-label' in el.attrib:
                    del el.attrib['data-toc-label']

                if self.use_anchors:
                    self.add_anchor(el, el.attrib["id"])
                if self.use_permalinks:
                    self.add_permalink(el, el.attrib["id"])
                    
        toc_tokens = nest_toc_tokens(toc_tokens)
        div = self.build_toc_div(toc_tokens)
        if self.marker:
            self.replace_marker(doc, div)

        self.replace_section_links(doc, toc_map)

        # serialize and attach to markdown instance.
        toc = self.md.serializer(div)
        for pp in self.md.postprocessors:
            toc = pp.run(toc)
        self.md.toc_tokens = toc_tokens
        self.md.toc_map = toc_map
        self.md.toc = toc

class NumberingTocExtension(TocExtension):
    TreeProcessorClass = NumberingTocTreeprocessor

    def __init__(self, **kwargs):
        # Overriding the base class's self.config is a nuisance. I'm doing it by creating a temporary instance and stealing the config dict out of that one.
        tempext = TocExtension()
        self.config = dict(tempext.config)

        self.config['number_top_start'] = [ 1, 'The index value of the first top-level section' ]
        self.config['header_link_label'] = [ 'section ', 'The label to add before internal links' ]

        # Skip the base class's __init__ and go straight to the grand-base!
        Extension.__init__(self, **kwargs)

    def reset(self):
        TocExtension.reset(self)
        self.md.toc_map = {}
