.PHONY: run test

run:
	python3 src/main.py

test:
	python3 -m unittest discover tests/

install:
	pip3 install -r requirements.txt