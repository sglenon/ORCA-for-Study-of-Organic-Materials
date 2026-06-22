.PHONY: install test notebooks-clean zip

install:
	python -m pip install -e .[dev]

test:
	pytest -q

notebooks-clean:
	jupyter nbconvert --clear-output --inplace notebooks/*.ipynb

zip:
	cd .. && zip -r ORCA-Reviewer.zip ORCA-Reviewer
