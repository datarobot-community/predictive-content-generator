.PHONY: copyright-check apply-copyright fix-licenses check-licenses
## Copyright checks
copyright-check:
	docker run -it --rm -v $(CURDIR):/github/workspace apache/skywalking-eyes header check

## Add copyright notice to new files
apply-copyright:
	docker run -it --rm -v $(CURDIR):/github/workspace apache/skywalking-eyes header fix

fix-licenses: apply-copyright

check-licenses: copyright-check

fix-lint:
	ruff format .
	ruff check . --fix

lint:
	ruff format --check .
	ruff check .
	mypy .

check-all: check-licenses lint
