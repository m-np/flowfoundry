.PHONY: env install lint test build publish publish-test

env:
	conda env create -f environment.yml || conda env update -f environment.yml

install:
	conda run -n flowfoundry pip install -e ".[dev]"

lint:
	conda run -n flowfoundry ruff check src tests

test:
	conda run -n flowfoundry pytest -q

build:
	rm -rf dist build *.egg-info || true
	conda run -n flowfoundry python -m build

publish:
	# Requires PYPI_TOKEN
	conda run -n flowfoundry twine upload -u __token__ -p $$PYPI_TOKEN dist/*

publish-test:
	conda run -n flowfoundry twine upload -r testpypi -u __token__ -p $$TEST_PYPI_TOKEN dist/*
