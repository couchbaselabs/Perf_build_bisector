# Makefile for Couchbase build bisector script

# Variables
PYTHON_VERSION := 3.12.0
VENV := env
PYTHON := $(VENV)/bin/python
SCRIPT := modified_script.py
REQUIREMENTS := requirements.txt
PATH := ${GOPATH}/bin:$(PATH):/usr/local/go/bin/

# Ensure pyenv is configured to use the correct Python version
.PHONY: pyenv
pyenv:
	export PYENV_ROOT="$$HOME/.pyenv" && \
	export PATH="$$PYENV_ROOT/bin:$$PATH" && \
	eval "$$(pyenv init --path)" && \
	pyenv install $$PYTHON_VERSION -s && \
	pyenv local $$PYTHON_VERSION

# Ensure virtual environment is set up
$(VENV): pyenv
	python -m venv $(VENV)

# Install dependencies
install: $(VENV) pyenv
	$(VENV)/bin/pip install -r $(REQUIREMENTS)

# Run the script
run: $(VENV) pyenv
	$(PYTHON) $(SCRIPT) \
		--good 7.6.2-3694 \
		--bad 7.6.2-3716 \
		--percentage 10 \
		--base_url https://showfast.sc.couchbase.com/api/v1/timeline/ \
		--metric ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv \
		--testfile transactions/collections/ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj.test

# Clean up
clean:
	rm -rf $(VENV)
