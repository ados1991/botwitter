VIRTUALENV:=pyvenv
PIP:=pip3

.PHONY: default
default:

.PHONY: venv
venv:
	$(VIRTUALENV) venv
	. venv/bin/activate && \
	$(PIP) install -r requirements.txt && \
	$(PIP) install -e .

.PHONY: clean
clean:
	rm -rf venv *.egg-info
	find . -type d -name __pycache__ -print0 | xargs -0 rm -rf

.PHONY: tree
tree:
	@tree -a -I 'venv|__pycache__|*.egg-info' --noreport
