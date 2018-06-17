FROM python:3-alpine

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system
COPY *.py ./

RUN addgroup -S dynip && adduser -S -G dynip dynip && chown -R dynip:dynip ./
USER dynip

EXPOSE 42514
ENTRYPOINT [ "gunicorn", "--bind", "0.0.0.0:42514", "app:app" ]
