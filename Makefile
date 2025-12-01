SHELL := /bin/bash

# Convenience variables
UVX := uvx
RUFF := $(UVX) ruff

fmt:
	$(RUFF) format
	$(RUFF) check --fix .

lint:
	$(RUFF) check .
