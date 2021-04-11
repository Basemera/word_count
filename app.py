from flask import Flask, logging, render_template, request, jsonify
import logging
import os
import requests
import operator
import re
import nltk
import json
import config
from flask_sqlalchemy import SQLAlchemy 
from api import api
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from rq import Queue
from rq.job import Job
from worker import conn

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'
                    .format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler()])

Logger = logging.getLogger()

# from models import Result

db = SQLAlchemy()


from models import *

def count_and_save_words(url):
    errors = []
    r = requests.get(url)
    if r:
        raw = BeautifulSoup(r.text, 'html.parser').get_text()
        nltk.data.path.append('./nltk_data/')  # set the path
        tokens = nltk.word_tokenize(raw)
        text = nltk.Text(tokens)
        # remove punctuation, count raw words
        nonPunct = re.compile('.*[A-Za-z].*')
        raw_words = [w for w in text if nonPunct.match(w)]
        raw_word_count = Counter(raw_words)
        # stop words
        no_stop_words = [w for w in raw_words if w.lower() not in stops]
        no_stop_words_count = Counter(no_stop_words)
        # results = sorted(
        #         no_stop_words_count.items(),
        #         key=operator.itemgetter(1),
        #         reverse=True
        # )[:10]
        from app import app
        with app.app_context():

            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
                return result.id
            except Exception as error:
                errors.append("Unable to add item to database.")
                return {"error": error}

def create_app():
    Logger.info(f'Starting app in {config.APP_ENV} enviroment')
    app = Flask(__name__)
    app.config.from_object('config')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    q = Queue(connection=conn)

    api.init_app(app)

    @app.route('/start', methods=['POST'])
    def get_counts():
        from app import count_and_save_words
        data = json.loads(request.data.decode())
        url = data["url"]

        if not url[:8].startswith(('https://', 'http://')):
            url = 'http://' + url
        job = q.enqueue_call(
            func=count_and_save_words, args=(url,), result_ttl=5000
        )
        return job.get_id()
        

    @app.route('/', methods=['GET', 'POST'])
    def index():
        errors = []
        results = {}
        if request.method == "POST":
            try:
                url = request.form['url']
                
            except:
                errors.append(
                    "Unable to get URL. Please make sure it is a valid URL"
                )
        return render_template('index.html', errors=errors, results=results)

    @app.route("/results/<job_key>", methods=['GET'])
    def get_results(job_key):
        job = Job.fetch(job_key, connection=conn)

        if job.is_finished:
            result = Result.query.filter_by(id=job.result).first()
            res = result.url
            results = sorted(
                result.result_no_stop_words.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:10]
            results.append(res)
            return jsonify(results), 200
        else:
            return "Nay!", 202


    # @app.route('/')
    # def hello_world():
    #     return "Hello World!"
    return app


app = create_app()
# db = SQLAlchemy(app)

# from models import Result

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     errors = []
#     results = []
#     if request.method == "POST":
#         try:
#             url = request.form['url']
#             r = requests.get(url)
#             print(r.text)
#             results.append(r.text)
#             if r:
#                 raw = BeautifulSoup(r.text, 'html.parser').get_text()
#                 nltk.data.path.append('./nltk_data/')  # set the path
#                 tokens = nltk.word_tokenize(raw)
#                 text = nltk.Text(tokens)
#                 # remove punctuation, count raw words
#                 nonPunct = re.compile('.*[A-Za-z].*')
#                 raw_words = [w for w in text if nonPunct.match(w)]
#                 raw_word_count = Counter(raw_words)
#                 # stop words
#                 no_stop_words = [w for w in raw_words if w.lower() not in stops]
#                 no_stop_words_count = Counter(no_stop_words)
#                 results = sorted(
#                         no_stop_words_count.items(),
#                         key=operator.itemgetter(1),
#                         reverse=True
#                 )
#                 try:
#                     result = Result(
#                         url=url,
#                         result_all=raw_word_count,
#                         result_no_stop_words=no_stop_words_count
#                     )
#                     db.session.add(result)
#                     db.session.commit()
#                 except:
#                     errors.append("Unable to add item to database.")

#         except:
#             errors.append(
#                 "Unable to get URL. Please make sure it is a valid URL"
#             )
#     return render_template('index.html', errors=errors, results=results)



if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
    # </td>
    # </tr>
    # <td>