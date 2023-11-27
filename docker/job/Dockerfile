FROM python:3.10.12-slim-bookworm

ENV DEBIAN_FRONTEND noninteractive

RUN apt update -y
RUN apt -y install sudo software-properties-common
RUN apt -y install build-essential \
    && apt -y install libpq-dev \
    && apt -y install wget \
    && apt -y install unzip \
    && apt -y install libgl1-mesa-glx ffmpeg libsm6 libxext6 tesseract-ocr
RUN apt-get install -y poppler-utils

RUN mkdir /usr/local/share/tessdata
RUN cd /usr/local/share/tessdata && \
    wget https://github.com/tesseract-ocr/tessdata_best/archive/refs/tags/4.1.0.zip

RUN cd /usr/local/share/tessdata && \
    unzip 4.1.0.zip && \
    mv tessdata_best-4.1.0/* . && \
    rm -rf tessdata_best-4.1.0 && \
    rm 4.1.0.zip

# Setting the data prefix
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /work

COPY poke_battle_logger ./poke_battle_logger
COPY tests ./tests
COPY config ./config
COPY scripts ./scripts
COPY data ./data
COPY template_images ./template_images
COPY Makefile poetry.lock pyproject.toml setup.cfg ./
RUN mkdir video /mnt /mnt/disks

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry
RUN poetry install --with dev,job

EXPOSE 11000

CMD ["make", "run_job_api"]
