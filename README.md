
# Glk, Glulx, and Blorb Specifications

These documents describe what was intended to be a universal interactive fiction platform. By the law of [XKCD 927][927], they did not wind up being universal. But they form important parts of the technology used by many IF tools.

[927]: https://xkcd.com/927/
[i7]: http://inform7.com/
[i6]: https://inform-fiction.org/Welcome.html

The copyrights of these documents are owned by the [Interaction Fiction Technology Foundation][iftf], a nonprofit which supports IF tools and resources. They are all licensed under a Creative Commons Attribution-Noncommercial-Share Alike 3.0 Unported License: [https://creativecommons.org/licenses/by-nc-sa/3.0](https://creativecommons.org/licenses/by-nc-sa/3.0).

These documents are managed by IFTF's [Archive Committee][archcom]. If you have questions or requests, please contact `<specs@ifarchive.org>`.

[iftf]: https://iftechfoundation.org/
[archcom]: https://iftechfoundation.org/committees/ifarchive/

The Glk, Glulx, and Blorb specifications were originally created by Andrew Plotkin.

### Glulx: A 32-Bit Virtual Machine for IF

Glulx is a spiritual successor to Infocom's Z-machine. It describes an imaginary general-purpose computer which is relatively easy to implement. [Inform 7][i7] is a well-known IF tool that generates Glulx game files.

(More information can be found on the [original Glulx home page][glulxpage].)

[glulxpage]: https://eblong.com/zarf/glulx/

### Glk: A Portable Interface Standard for IF

Glk is an API which abstracts the common I/O operations of IF programs (games and interpreters). Glulx uses Glk as its native I/O layer, but other IF systems have been ported to Glk as well.

(More information can be found on the [original Glk home page][glkpage].)

[glkpage]: https://eblong.com/zarf/glk/

### Blorb: An IF Resource Collection Format Standard

Blorb is a packaging format which wraps up an IF game file and its resources (images, sounds, metadata) into one file. Glulx games are commonly distributed in Blorb format.

(More information can be found on the [original Blorb home page][blorbpage].)

[blorbpage]: https://eblong.com/zarf/blorb/

## Rebuilding the documents

This repository includes the current versions of the spec documents in Markdown. It also contains a Python script to render the documents into HTML and from there into PDF.

(The Markdown can be viewed with a standard Markdown viewer. If you're reading this in the GitHub repo, the links above will do this! However, the `makehtml.py` script will add such amenities as a table of contents, named internal links, and a nice stylesheet.)

Building the HTML requires Python3 and the [Markdown package][pymarkdown].

[pymarkdown]: https://github.com/Python-Markdown/markdown

Building the PDF requires the [wkhtmltopdf tool][wkhtmltopdf].

[wkhtmltopdf]: https://wkhtmltopdf.org/

