VERSION=learn
TEST_OPTIONS=-x

clean:
	rm -f MANIFEST README TAGS
	find . -name "*~" | xargs rm

help:
	@echo "targets in this makefile:"
	@echo "   clean      - remove generated files"
	@echo "   desc       - set up .git/description"
	@echo "   help       - provide this list"
	@echo "   green      - use green to run the tests"
	@echo "   nose       - use nosetests to run the tests"
	@echo "   py.test    - use py.test to run the tests"
	@echo "   install    - pip install dist/backscratcher-$(VERSION).tar.gz"
	@echo "   readme     - cp README.md README"
	@echo "   refresh    - refresh and upgrade the distro"
	@echo "   retag      - remove TAGS and remake it"
	@echo "   sdist      - build the distro"
	@echo "   tags       - create a TAGS file for emacs"
	@echo "   uninstall  - remove backscratcher from current system"
	@echo "   up         - pip install --upgrade dist/backscratcher-$(VERSION).tar.gz"
	@echo "   utest      - use unittest to run the tests"
	@echo "   version    - git describe > .bscr_version"

desc:
	echo "backscratcher" > .git/description

green:
	green $(TEST_OPTIONS)

nose:
	nosetests -c nose.cfg $(TEST_OPTIONS)

py.test: up
	py.test $(TEST_OPTIONS)

install:
	pip install dist/backscratcher-$(VERSION).tar.gz

uninstall:
	pip uninstall backscratcher

readme:
	cp README.md README

refresh: sdist up

sdist: readme
	find . -name "*.pyc" | xargs rm
	python setup.py sdist -m MANIFEST

retag:
	rm TAGS
	find . -name "*.py" | xargs etags

tags:
	find . -name "*.py" | xargs etags

up:
	pip install --upgrade .

utest:
	for fn in `ls test/test_*.py`; do echo ==== $$fn ====; $$fn -v; done

version:
	git describe > .bscr_version
