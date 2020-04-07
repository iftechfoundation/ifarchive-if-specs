
HTMLTARGETS = dist/Glk-Spec.html dist/Glulx-Spec.html dist/Glulx-Inform-Tech.html dist/Blorb-Spec.html
PDFTARGETS = dist/Glk-Spec.pdf dist/Glulx-Spec.pdf dist/Glulx-Inform-Tech.pdf dist/Blorb-Spec.pdf

html: $(HTMLTARGETS)

pdf: $(PDFTARGETS)

dist/%.html : %.md
	python3 tools/makehtml.py $< tools/template.html $@

dist/%.pdf : dist/%.html
	wkhtmltopdf -q -s Letter $< $@

clean:
	-rm -f $(HTMLTARGETS)
