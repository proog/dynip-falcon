FROM python:3-slim

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

COPY wsgi.py ./
COPY dynip dynip/

EXPOSE 80
ENTRYPOINT [ "gunicorn", "wsgi" ]
CMD [ "--bind", "0.0.0.0:80" ]
