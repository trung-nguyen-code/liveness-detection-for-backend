###############################################
# Base Image
###############################################
FROM python:3.9.5-slim as python-base

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PIP_NO_CACHE_DIR=off 
ENV PIP_DISABLE_PIP_VERSION_CHECK=on 
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
# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN pip install --upgrade pip poetry==1.4.2

WORKDIR $PYSETUP_PATH

COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev --no-root

###############################################
# Production Image
###############################################
FROM python-base as production

WORKDIR /ai

# copy only necessary files from builder image
COPY --from=builder-base $PYSETUP_PATH/.venv $PYSETUP_PATH/.venv
COPY --from=builder-base $PYSETUP_PATH/pyproject.toml $PYSETUP_PATH/poetry.lock ./
COPY ./ ./

RUN chmod +x ./uvicorn.sh
EXPOSE 5555

CMD ["./uvicorn.sh"]
