FROM kennethreitz/pipenv

COPY *.py ./
ENV PYTHONUNBUFFERED 1
EXPOSE 42514

CMD [ "gunicorn", "--bind", "0.0.0.0:42514", "app:app" ]
