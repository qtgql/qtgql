.PHONY : test

test:
	pytest tests --cov=qtgql --cov-report=xml --cov-append
