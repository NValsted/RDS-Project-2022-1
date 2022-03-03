backup_dir := backup
docker_image := rct/main:latest

build-image:
ifeq ($(OS),Windows_NT)
	docker build --no-cache . -t ${docker_image}
else
	sudo docker build --no-cache . -t ${docker_image}
endif

run-image-interactive:
	docker run --rm -it ${docker_image}

setup:
	mkdir -p ${backup_dir}
	poetry install
	poetry run python setup.py

run:
	poetry run python main.py

report:
	poetry run python report.py
