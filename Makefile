clean:
	find . -name "*~" | xargs rm

sdist:
	find . -name "*.pyc" | xargs rm
	python setup.py sdist -m MANIFEST

install:
	pip install dist/backscratcher-learn.tar.gz

upgrade:
	pip install --upgrade dist/backscratcher-learn.tar.gz

