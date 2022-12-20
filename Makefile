.PHONY : test

test:
	poetry run pytest --cov=qter --cov-report=xml
