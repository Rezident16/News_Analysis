from flask import Blueprint
from .news_helpers import fetch_news, estimate_news_sentiment

news_routes = Blueprint('news', __name__)

@news_routes.route('/<symbol>/<stock_name>')
def get_news(symbol, stock_name):
    print(symbol)
    news = fetch_news(symbol)
    news_and_sentiment = estimate_news_sentiment(news, symbol, stock_name)
    return news_and_sentiment
