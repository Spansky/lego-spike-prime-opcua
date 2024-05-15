# Makefile for Python Project

# Variables
VENV_DIR = .venv
PYTHON = python
PIP = $(VENV_DIR)/bin/pip
ACTIVATE = $(VENV_DIR)/bin/activate
REQUIREMENTS = requirements.txt
REQUIREMENTS_TIMESTAMP = .requirements_installed

# Default target
all: install

# Create virtual environment
$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)

# Install dependencies only if requirements.txt has changed
$(REQUIREMENTS_TIMESTAMP): $(REQUIREMENTS) $(VENV_DIR)
	$(PIP) install -r $(REQUIREMENTS)
	touch $(REQUIREMENTS_TIMESTAMP)

# Install target depends on the timestamp file
install: $(REQUIREMENTS_TIMESTAMP)

# Run the application
run: install
	bash -c 'source $(ACTIVATE) && $(PYTHON) src/main.py'

# Lint the project
lint: install
	$(PIP) install flake8
	bash -c 'source $(ACTIVATE) && flake8 src/.'

# Clean the project
clean:
	rm -rf $(VENV_DIR) $(REQUIREMENTS_TIMESTAMP)

# Remove Python bytecode files
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

# Clean all
clean-all: clean clean-pyc

.PHONY: all install run lint clean clean-pyc clean-all
