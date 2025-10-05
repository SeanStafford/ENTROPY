#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = entropy
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = python
PACKAGE_MANAGER = pip

#################################################################################
# INSTALLATION COMMANDS                                                         #
#################################################################################

## Install Python Dependencies
.PHONY: install
install:
	pip install -e .
	@echo ">>> Base dependencies installed."

## Install development dependencies
.PHONY: install-dev
install-dev:
	pip install -e ".[dev,eval]"
	@echo ">>> Development and evaluation dependencies installed"

#################################################################################
# CODE HYGEINE COMMANDS                                                         #
#################################################################################

## Delete all compiled Python files and caches
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@echo ">>> Cleaned Python cache files"

## Lint code using ruff (use `make format` to auto-fix)
.PHONY: lint
lint:
	ruff check entropy
	ruff format --check entropy
	@echo ">>> Linting complete"

## Format source code with ruff
.PHONY: format
format:
	ruff check --select I --fix entropy  # Fix import sorting
	ruff format entropy
	@echo ">>> Code formatted"

#################################################################################
# Self Documenting Boilerplate                                                  #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('ENTROPY - Financial Intelligence System\n'); \
print('Available commands:\n'); \
print('\n'.join(['{:20}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)