from flask import Flask, render_template, request
from pymongo import MongoClient
from datetime import datetime
import re
from MainInverter import main
import os

app = Flask(__name__)

def fetchDate():
    return datetime.now().strftime("%Y_%m_%d")

mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    raise ValueError("❌ MONGO_URI not set. Please configure in Render dashboard.")

client = MongoClient(mongo_uri)
db = client["MovieHub"]
# collection = db[f"movieList_{fetchDate()}"]
collection = db[f"movieList_2025_09_04"]

@app.route('/', methods=['GET'])
def showMovies():
    per_page = 16
    page = int(request.args.get('page', 1))
    query = request.args.get('query', '').strip()
    skip = (page - 1) * per_page

    print(query)

    if query:
        escaped_term = re.escape(query)
        regex = f".*{escaped_term}.*"
        filter_query = {"movieName": {"$regex": regex, "$options": "i"}}
    else:
        filter_query = {}

    movies = list(collection.find(filter_query, {"_id": 0}).sort("scrapeDate", -1).skip(skip).limit(per_page))
    total_movies = collection.count_documents(filter_query)
    total_pages = (total_movies + per_page - 1) // per_page

    return render_template(
        'index.html',
        movies=movies,
        query=query,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        total_movies=total_movies
    )

@app.route('/download')
def downloadMovie():
    url = request.args.get('link', '').strip()
    name = request.args.get('name', '').strip()
    downloadOptions = main(url)
    return render_template('download.html', options=downloadOptions, name=name)

if __name__ == '__main__':
    app.run(debug=True)
