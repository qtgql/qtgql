.PHONY : test

test:
	poetry run pytest --cov=qtier --cov-report=xml
