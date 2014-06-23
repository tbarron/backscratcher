VERSION=learn

clean:
	rm -f MANIFEST README TAGS
	find . -name "*~" | xargs rm

help:
	@echo "targets in this makefile:"
	@echo "   clean      - remove generated files"
	@echo "   help       - provide this list"
	@echo "   green      - use green to run the tests"
	@echo "   nose       - use nosetests to run the tests"
	@echo "   install    - pip install dist/backscratcher-$(VERSION).tar.gz"
	@echo "   readme     - cp README.md README"
	@echo "   refresh    - refresh and upgrade the distro"
	@echo "   sdist      - build the distro"
	@echo "   tags       - create a TAGS file for emacs"
	@echo "   upgrade    - pip install --upgrade dist/backscratcher-$(VERSION).tar.gz"
	@echo "   utest      - use unittest to run the tests"

green:
	green -v test

nose:
	nosetests -v -c nose.cfg test/test_*.py

install:
	pip install dist/backscratcher-$(VERSION).tar.gz

readme:
	cp README.md README

refresh: sdist upgrade

sdist: readme
	find . -name "*.pyc" | xargs rm
	python setup.py sdist -m MANIFEST

tags:
	find . -name "*.py" | xargs etags

upgrade:
	pip install --upgrade dist/backscratcher-$(VERSION).tar.gz

utest:
	for fn in `ls test/test_*.py`; do echo ==== $$fn ====; $$fn -v; done
