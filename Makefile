.PHONY : test

test:
	pytest --cov=qtier --cov-report=xml
