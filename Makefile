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

## Create virtual environment (if it doesn't exist)
.PHONY: venv
venv:
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON_INTERPRETER) -m venv .venv; \
		echo ">>> Virtual environment created at .venv"; \
		echo ">>> Activate with: source .venv/bin/activate"; \
	else \
		echo ">>> Virtual environment already exists at .venv"; \
	fi

## Install Python Dependencies
.PHONY: install
install: venv
	pip install -e .
	@echo ">>> Base dependencies installed."

## Install development dependencies
.PHONY: install-dev
install-dev: venv
	pip install -e ".[dev,eval]"
	@echo ">>> Development and evaluation dependencies installed"

## Install all dependencies including local ML models
.PHONY: install-all
install-all: venv
	pip install -e ".[dev,eval,local]"
	@echo ">>> All dependencies including local ML models installed"

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
# UTILITY COMMANDS                                                              #
#################################################################################

## Show recently modified files (like tree + ls -ltr)
.PHONY: recent
recent:
	@find . -type f -not -path '*/\.*' -not -path '*/__pycache__/*' -not -path '*/venv/*' -not -path '*/.venv/*' -printf '%T@ %p\n' | sort -n | tail -20 | perl -MTime::Piece -MTime::Seconds -nE 'chomp; ($$t, $$f) = split / /, $$_, 2; $$now = time; $$diff = $$now - int($$t); if ($$diff < 60) { $$ago = sprintf "%ds ago", $$diff } elsif ($$diff < 3600) { $$ago = sprintf "%dm ago", $$diff/60 } elsif ($$diff < 86400) { $$ago = sprintf "%dh ago", $$diff/3600 } else { $$ago = sprintf "%dd ago", $$diff/86400 } printf "%-12s %s\n", $$ago, $$f'

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