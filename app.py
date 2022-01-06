import os

from flask import Flask, render_template, request
from flask_cors import cross_origin

from WikiScraper import WikiScraper
from loggerClass import getLog
from MongoDBops import DBops

logger = getLog('WikiScraper.py')

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/Result', methods=['POST', 'GET'])  # route to display results
@cross_origin()
def index():
    if request.method == 'POST':
        try:

            try:
                s1 = request.form['content']
                logger.info("Search string received")
                s2 = s1.split(' ')
                s2 = [i.capitalize() for i in s2]
                searchString = '_'.join(s2)
                logger.info("Search string treated")
            except Exception as e:
                print(f"{searchString}- error try again: {e}")

            mongoClient = DBops(username='Sidkapoor', password='mongodb')
            logger.info("DB connection established")
            if mongoClient.findDocument(searchString) is not None:
                # logger.info("records already present in db")
                result = mongoClient.findDocument(searchString)
                # logger.info("Records found")
                return render_template('results.html', result=result)
            else:
                logger.info("Records not found in db")
                result = WikiScraper.wiki_collection(searchString)
                logger.info("Search performed")
                mongoClient.insertDoc(result)
                logger.info("Records stored in db")
                return render_template('results.html', result=result)
        except Exception as e:
            logger.info(f"{e} no results found, routed back to index")
            return render_template('index.html', exception="Invalid search, try again")
    else:
        logger.info("POST method not used, routed back to index")
        return render_template('index.html', exception='Use POST method')


# DEFAULT_PORT = 1234
# port = int(os.getenv('PORT', DEFAULT_PORT))
if __name__ == "__main__":
    app.run()
