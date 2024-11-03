import os
import logging
from flask import Flask, jsonify
from .api.news_routes import news_routes

app = Flask(__name__)
app.register_blueprint(news_routes, url_prefix='/api/news')

# Set up logging
# logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    app.logger.info("Index route accessed")
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
