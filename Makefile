# Author: Aditya Dogra
.PHONY: setup setup-base setup-mcp run daily daily-updates mcp test

setup:
	python3 scripts/bootstrap.py --extras full

setup-base:
	python3 scripts/bootstrap.py --extras ""

setup-mcp:
	python3 scripts/bootstrap.py --extras mcp

run:
	. .venv/bin/activate && ietf-wg-agent

daily:
	. .venv/bin/activate && ietf-wg-daily

daily-updates:
	. .venv/bin/activate && ietf-wg-daily-updates --once

mcp:
	. .venv/bin/activate && ietf-wg-mcp

test:
	. .venv/bin/activate && python -m pytest -q tests
