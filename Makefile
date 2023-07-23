.PHONY: clean clean-model clean-pyc docs help init init-docker create-container start-container jupyter test lint profile clean clean-data clean-docker clean-container clean-image sync-from-source sync-to-source
.DEFAULT_GOAL := help

###########################################################################################################
## VARIABLES
###########################################################################################################
export PROJECT_NAME=poke_battle_logger
export TARGET=
export DOCKER=docker
export PRINT_HELP_PYSCRIPT
export PYTHON=poetry run python
export PYTHONPATH=$PYTHONPATH:$(pwd)
export SERVER_IMAGE_NAME=$(PROJECT_NAME)-image-server
export CONTAINER_NAME=$(PROJECT_NAME)-container
export SERVER_DOCKERFILE=docker/server/Dockerfile
export DOCKER_BUILDKIT=1
export ENV=local
export LOCAL_TESSDATA_PREFIX=/opt/brew/Cellar/tesseract/5.3.0_1/share/tessdata_best/
export LOCAL_GOOGLE_APPLICATION_CREDENTIALS=.credentials/google-cloud-credential.json
export API_HOST_PORT=8001
export API_CONTAINER_PORT=10000

###########################################################################################################
## Specific Target "poke_battle_logger"
###########################################################################################################

extract-data: # extract battle data from video file
	$(PYTHON) poke_battle_logger/batch/extract_data.py \
	--video_id $(VIDEO_ID) \
	--trainer_id $(TRAINER_ID) \
	--lang $(LANG)

build-pokemon-faiss-index: # build pokemon faiss index
	$(PYTHON) poke_battle_logger/batch/build_pokemon_faiss_index.py

build-pokemon-multi-name-dict: # build pokemon multi name dict
	$(PYTHON) poke_battle_logger/batch/build_pokemon_name_dict.py

run_dashboard:
	cd poke_battle_logger_vis && yarn run dev

run_api:
	ENV=$(ENV) poetry run uvicorn poke_battle_logger.api.app:app --host 0.0.0.0 --port $(API_CONTAINER_PORT)

run_api_in_cloud_run:
	ENV=production uvicorn poke_battle_logger.api.app:app --host 0.0.0.0 --port $(API_CONTAINER_PORT)

run_api_local:
	TESSDATA_PREFIX=$(LOCAL_TESSDATA_PREFIX) \
	GOOGLE_APPLICATION_CREDENTIALS=$(LOCAL_GOOGLE_APPLICATION_CREDENTIALS) \
	poetry run uvicorn poke_battle_logger.api.app:API_CONTAINER_PORT

run_api_local_use_postgres:
	ENV=production \
	TESSDATA_PREFIX=$(LOCAL_TESSDATA_PREFIX) \
	GOOGLE_APPLICATION_CREDENTIALS=$(LOCAL_GOOGLE_APPLICATION_CREDENTIALS) \
	poetry run uvicorn poke_battle_logger.api.app:app

###########################################################################################################
## GENERAL TARGETS
###########################################################################################################

test:
	poetry run pytest -vvv

test_local:
	TESSDATA_PREFIX=$(LOCAL_TESSDATA_PREFIX) poetry run pytest -vvv

format: ## format style with pysen
	poetry run pysen run format

lint: ## check style with pysen
	poetry run pysen run lint

test-in-docker: ## run test cases in tests directory in docker
	$(DOCKER) run --rm $(SERVER_IMAGE_NAME) make test

lint-in-docker: ## check style with flake8 in docker
	$(DOCKER) run --rm $(SERVER_IMAGE_NAME) make lint

jupyter: ## start Jupyter Notebook server
	poetry run jupyter-notebook --ip=0.0.0.0 --port=${JUPYTER_CONTAINER_PORT}

init-docker-server: ## initialize docker image
	$(DOCKER) build -t $(SERVER_IMAGE_NAME) -f $(SERVER_DOCKERFILE) .

create-container-no-mount: ## create docker container for development
	$(DOCKER) run --rm -it -p $(API_HOST_PORT):$(API_CONTAINER_PORT) \
    --name $(CONTAINER_NAME) $(SERVER_IMAGE_NAME) /bin/bash

create-container-mount: ## create docker container for development
	$(DOCKER) run --rm -it -v $(PWD):/work -p $(API_HOST_PORT):$(API_CONTAINER_PORT) \
    --name $(CONTAINER_NAME) $(SERVER_IMAGE_NAME) /bin/bash
