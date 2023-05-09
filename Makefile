.PHONY : test

test:
	pytest tests --cov=qtgql --cov-report=xml --cov-append


serve_tests:
	poetry run python -m tests.scripts.tests_server
