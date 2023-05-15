.PHONY : test generate_test_files serve_tests

test:
	pytest tests --cov=qtgql --cov-report=xml --cov-append


serve_tests:
	poetry run python -m tests.scripts.tests_server

generate_test_files:
	poetry run python -m tests.test_codegen.testcases
