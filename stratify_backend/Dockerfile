FROM python:3.10-slim-buster as builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /stratify_backend

COPY pyproject.toml poetry.lock ./

# Poetry complains if the README is missing, so a dummy one is created
RUN touch README.md

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.10-slim-buster as runtime

ENV VIRTUAL_ENV=/stratify_backend/.venv \
    PATH="/stratify_backend/.venv/bin:$PATH"

WORKDIR /stratify_backend

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . .

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
