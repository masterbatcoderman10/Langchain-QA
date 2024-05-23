# Makefile

# Set shell to bash
SHELL := /bin/bash

# Default target
all: venv

# Create the virtual environment
venv:
	python3 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	deactivate
	touch .env

# Clean up the virtual environment
.PHONY: clean
clean:
	rm -rf venv