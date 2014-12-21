.PHONY: docs
.SILENT: init-devel test test-tox test-coverage

all: clean test

clean-docs:
	-rm -rfv docs/_build

clean-tox:
	-rm -rfv .tox

clean-coverage:
	-rm .coverage*
	-rm coverage.xml
	-rm -rfv htmlcov

clean-pyc:
	-find . -path './.tox' -prune -or \
		-name '__pycache__' -exec rm -rv {} +
	-find . -path './.tox' -prune -or \
		\( -name '*.pyc' -or -name '*.pyo' \) -exec rm -rv {} +

clean-all: clean-tox clean-docs clean

clean: clean-pyc clean-coverage
	-rm -rv build dist *.egg-info

sync-dependencies:
	pip install -r requirements/develop.txt

test:
	py.test -sv test_chronometer.py

test-tox:
	tox

test-coverage:
	coverage erase
	coverage run --source=chronometer --branch -m pytest -v
	coverage report
	coverage xml

audit:
	flake8 chronometer

docs:
	$(MAKE) -C docs html
