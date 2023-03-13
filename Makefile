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
export ENV=staging
export TESSDATA_PREFIX=/opt/brew/Cellar/tesseract/5.3.0_1/share/tessdata/

###########################################################################################################
## Specific Target "poke_battle_logger"
###########################################################################################################

extract-data: # extract battle data from video file
	TESSDATA_PREFIX=$(TESSDATA_PREFIX) \
	$(PYTHON) poke_battle_logger/batch/extract_data.py \
	--video_id $(VIDEO_ID)


###########################################################################################################
## GENERAL TARGETS
###########################################################################################################

jupyter: ## start Jupyter Notebook server
	poetry run jupyter-notebook --ip=0.0.0.0 --port=${JUPYTER_CONTAINER_PORT}

lint: ## check style with pysen
	poetry run pysen run lint

format: ## format style with pysen
	poetry run pysen run format

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
