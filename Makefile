# Makefile wrapper for common tasks

PYTHON ?= python3

test:
	$(PYTHON) -m unittest -v tests

lint:
	pylint dircolors tests setup.py

dist:
	rm -rf dist
	$(PYTHON) setup.py sdist bdist_wheel

venv:
	$(PYTHON) -m venv venv
	. ./venv/bin/activate; pip install -U pip ipython; pip install -r requirements-dev.txt

clean:
	find . -path ./venv -prune -o -name __pycache__ -exec rm -rf {} \; -prune
	rm -rf build dist *.egg-info

distclean: clean
	rm -rf venv

.PHONY: test lint dist venv clean distclean
.NOTPARALLEL:
