.PHONY : test generate_test_files serve_tests conan_install



serve_tests:
	poetry run python -m tests.scripts.tests_server

# TODO should run the generate command directly
generate_test_files:
	poetry run python -m tests.test_codegen.generate

test:
	pytest tests --cov=qtgql --cov-report=xml --cov-append
