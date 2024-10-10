.PHONY: copyright-check apply-copyright fix-licenses check-licenses
## Copyright checks
copyright-check:
	docker run -it --rm -v $(CURDIR):/github/workspace apache/skywalking-eyes header check

## Add copyright notice to new files
apply-copyright:
	docker run -it --rm -v $(CURDIR):/github/workspace apache/skywalking-eyes header fix

fix-licenses: apply-copyright

check-licenses: copyright-check

check-lint:
	ruff format --check recipe-bob/.
	ruff check recipe-bob/.

lint:
	ruff format recipe-bob/.
	ruff check recipe-bob/. --fix

run_app_locally:
	cd recipe-bob/include/app && streamlit run app.py
