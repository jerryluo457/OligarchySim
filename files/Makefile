.PHONY: run clean venv

VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install numpy

run: venv
	$(PYTHON) simulation.py

clean:
	rm -rf $(VENV) __pycache__
