FROM python:3.10.10-slim-bullseye

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -y \
    && apt-get -y install build-essential \
    && apt-get -y install libpq-dev \
    && apt-get -y install libtesseract-dev \
    && apt-get -y install tesseract-ocr \
    && apt-get -y install wget \
    && apt-get -y install unzip \
    && apt-get -y install libgl1-mesa-glx ffmpeg libsm6 libxext6

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
COPY data ./data
COPY template_images ./template_images
COPY Makefile poetry.lock pyproject.toml setup.cfg ./
RUN mkdir video

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir poetry awscli
RUN poetry export --dev -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt

EXPOSE 10000

CMD ["make", "run_api_in_cloud_run"]
