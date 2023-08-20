.PHONY : test generate_test_files serve_tests conan_install



serve_tests:
	poetry run python -m tests.scripts.tests_server

test:
	poetry run xvfb-run -a pytest tests --cov=qtgqlcodegen --cov-report=xml --cov-append
