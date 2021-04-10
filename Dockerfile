FROM python:3.7.7

ADD ./TODO_FLASK_APP
WORKDIR /TODO_FLASK_APP

RUN pip install --system --skip-lock

RUN pip install gunicorn[gevent]

EXPOSE 5000

CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:5000 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info