backup_dir := backup

setup:
	mkdir -p ${backup_dir}
	poetry install
	poetry run python setup.py

run:
	poetry run python main.py

run_all:
	make setup
	make run
