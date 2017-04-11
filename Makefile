TESTS = $(wildcard tests/*.py)

test:
	python3 -m unittest $(TESTS)

demo:
	@python3 demo.py
