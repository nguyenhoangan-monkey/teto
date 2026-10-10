.PHONY: setup run clean test

# Default python executable
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin

# For Windows OS compatibility in GNU Make
ifeq ($(OS), Windows_NT)
	BIN = $(VENV)/Scripts
endif

# 1. Create venv and install dependencies
setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

# 2. Run the main extraction pipeline inside the venv
run:
	$(BIN)/python src/main_extract.py

# 3. Clean up virtual environment and python cache files
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
