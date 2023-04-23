.PHONY: clean clean-model clean-pyc docs help init init-docker create-container start-container jupyter test lint profile clean clean-data clean-docker clean-container clean-image sync-from-source sync-to-source
.DEFAULT_GOAL := help

###########################################################################################################
## VARIABLES
###########################################################################################################
export TARGET=
export DOCKER=docker
export PRINT_HELP_PYSCRIPT
export PYTHON=poetry run python
export PYTHONPATH=$PYTHONPATH:$(pwd)
export IMAGE_NAME=$(PROJECT_NAME)-image
export CONTAINER_NAME=$(PROJECT_NAME)-container
export DOCKERFILE=docker/Dockerfile
export JUPYTER_HOST_PORT=8080
export JUPYTER_CONTAINER_PORT=8080
export DOCKER_BUILDKIT=1
export ENV=local
export TESSDATA_PREFIX=/opt/brew/Cellar/tesseract/5.3.0_1/share/tessdata_best/

###########################################################################################################
## Specific Target "poke_battle_logger"
###########################################################################################################

extract-data: # extract battle data from video file
	TESSDATA_PREFIX=$(TESSDATA_PREFIX) \
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
	TESSDATA_PREFIX=$(TESSDATA_PREFIX) poetry run uvicorn poke_battle_logger.api.app:app --reload

###########################################################################################################
## GENERAL TARGETS
###########################################################################################################

test:
	TESSDATA_PREFIX=$(TESSDATA_PREFIX) poetry run pytest -vvv

format: ## format style with pysen
	poetry run pysen run format

lint: ## check style with pysen
	poetry run pysen run lint

test-in-docker: ## run test cases in tests directory in docker
	$(DOCKER) run --rm $(IMAGE_NAME) make test

lint-in-docker: ## check style with flake8 in docker
	$(DOCKER) run --rm $(IMAGE_NAME) make lint

jupyter: ## start Jupyter Notebook server
	poetry run jupyter-notebook --ip=0.0.0.0 --port=${JUPYTER_CONTAINER_PORT}

init-docker: ## initialize docker image
	$(DOCKER) build -t $(IMAGE_NAME) -f $(DOCKERFILE) .

create-container-no-mount: ## create docker container for development
	$(DOCKER) run --rm -it -p $(JUPYTER_HOST_PORT):$(JUPYTER_CONTAINER_PORT) -p $(API_HOST_PORT):$(API_CONTAINER_PORT) \
    --name $(CONTAINER_NAME) --memory=64g --cpus="16" $(IMAGE_NAME) /bin/bash

create-container-mount: ## create docker container for development
	$(DOCKER) run --rm -it -v $(PWD):/work -p $(JUPYTER_HOST_PORT):$(JUPYTER_CONTAINER_PORT) -p $(API_HOST_PORT):$(API_CONTAINER_PORT) \
    --name $(CONTAINER_NAME) --memory=64g --cpus="16" $(IMAGE_NAME) /bin/bash

clean-model:
	rm -rf model/*.json model/*.pth

cloud-build:
	gcloud builds submit --config=cloudbuild.yaml --substitutions=_TAG=$(IMAGE_TAG)
