.PHONY : test

test:
	pytest --cov=qtgql --cov-report=xml
