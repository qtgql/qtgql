.PHONY : test generate_test_files serve_tests setup_repo



serve_tests:
	poetry run python -m tests.scripts.tests_server

generate_test_files:
	poetry run python -m tests.test_codegen.testcases

setup_repo:
	mkdir "3rdParty/Qt" -p
	cd ..
	poetry run aqt install-qt linux desktop 6.5.0 gcc_64 --outputdir ./3rdParty/Qt -m qtwebsockets
	cd tests && mkdir build -p
	cd ..
	make generate_test_files


test:
	pytest tests --cov=qtgql --cov-report=xml --cov-append
