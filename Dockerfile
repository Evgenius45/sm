FROM python:3.11 AS requirements-stage
WORKDIR /tmp

RUN pip install poetry
RUN poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11

WORKDIR /api_app

COPY --from=requirements-stage /tmp/requirements.txt /api_app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api_app/requirements.txt

COPY api_app ./api_app

CMD ["uvicorn", "api_app.main:app", "--host", "0.0.0.0", "--port", "8000"]

