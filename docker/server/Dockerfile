FROM python:3.10.9-slim-bullseye

RUN apt-get update -y \
    && apt-get -y install build-essential \
    && rm -rf /var/lib/apt/lists

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /work

COPY poke_battle_logger ./poke_battle_logger
COPY scripts ./scripts
COPY tests ./tests
COPY sql ./sql
COPY config ./config
COPY data ./data
COPY template_images ./template_images
COPY Makefile poetry.lock pyproject.toml setup.cfg ./

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir poetry awscli
RUN poetry config installer.parallel false
RUN poetry install

CMD ["/bin/bash"]
