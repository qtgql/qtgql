.PHONY : test

test:
	pytest tests --cov=qtgql --cov-report=xml
