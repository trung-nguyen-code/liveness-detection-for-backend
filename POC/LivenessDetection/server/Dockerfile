###############################################
# Base Image
###############################################
FROM python:3.9.6-slim as python-base

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PIP_NO_CACHE_DIR=off 
ENV PIP_DISABLE_PIP_VERSION_CHECK=on 
ENV PIP_DEFAULT_TIMEOUT=100 
ENV POETRY_VERSION=1.1.8
# make poetry install to this location
ENV POETRY_HOME="/opt/poetry" 
ENV POETRY_VIRTUALENVS_IN_PROJECT=true 
# do not ask any interactive question
ENV POETRY_NO_INTERACTION=1 
# paths
# this is where our requirements + virtual environment will live
ENV PYSETUP_PATH="/opt/pysetup" 
ENV VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Builder Image
###############################################
FROM python-base as builder-base
RUN apt-get update && apt-get install --no-install-recommends \
    -y curl build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
COPY get-poetry.py ./
RUN python get-poetry.py

WORKDIR $PYSETUP_PATH

COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev

###############################################
# Production Image
###############################################
FROM python-base as production

WORKDIR $PYSETUP_PATH

# copy in our built poetry virtual env
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

COPY . /liveness

WORKDIR /liveness

EXPOSE 5555

CMD ["./uvicorn.sh"]
