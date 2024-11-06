from datetime import datetime, timedelta
from collections import Counter
from torch import device
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import torch
from alpaca_trade_api import REST
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

# device = "mps" if torch.backends.mps.is_available() else ("cuda:0" if torch.cuda.is_available() else "cpu")
device = 0 if torch.cuda.is_available() else -1

finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer, device=device)

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
}

api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

DATE_FORMAT = '%Y-%m-%d'

def fetch_news(stock):
    today = datetime.now().date()
    week_prior = today - timedelta(days=7)
    news_list = api.get_news(stock, end=today.strftime(DATE_FORMAT), start=week_prior.strftime(DATE_FORMAT), include_content=True)
    
    news_dicts = []
    for news in news_list:
        news_dict = {
            "author": news.author,
            "content": news.content,
            "created_at": news.created_at,
            "headline": news.headline,
            "id": news.id,
            "images": news.images,
            "source": news.source,
            "summary": news.summary,
            "symbols": news.symbols,
            "updated_at": news.updated_at,
            "url": news.url
        }
        news_dicts.append(news_dict)
    
    return news_dicts

def estimate_news_sentiment(news, symbol, stock_name):
    news_and_sentiment = []
    content = ""
    for text in news:
        if text["summary"]:
            content = check_paragraph(text["summary"], symbol, stock_name)
            content = text["summary"]
        else:
            content = text["summary"] if text["summary"] else text["headline"]
        
        result = nlp_content(content)
        probability, sentiment = result
        newsObj = {
            "author": text['author'],
            "created_at": text['created_at'],
            "updated_at": text['updated_at'],
            "headline": text['headline'],
            "news_id": text['id'],
            "image": text['images'][0]["url"] if text['images'] else None,
            "source": text['source'],
            "symbols": text['symbols'],
            "summary": text['summary'],
            "url": text['url'],
            "probability": probability,
            "sentiment": sentiment
        }
        news_and_sentiment.append(newsObj)
    return news_and_sentiment

def nlp_content(content):
    try:
        result = nlp(content)
        probability = result[0]["score"]
        sentiment = result[0]["label"]
    except Exception as e:
        print(f"Error processing full text: {e}")
        sentences = content.split('.')
        probabilities = []
        sentiments = []
        for i in range(0, len(sentences), 3):  # Analyze 3 sentences at a time
            chunk = '.'.join(sentences[i:i+3])
            try:
                result = nlp(chunk)
                probabilities.append(result[0]["score"])
                sentiments.append(result[0]["label"])
            except Exception as e:
                print(f"Error processing chunk: {e}")

        if probabilities:
            probability = sum(probabilities) / len(probabilities)
            sentiment = Counter(sentiments).most_common(1)[0][0]
        else:
            probability = 0
            sentiment = "neutral"

    return probability, sentiment

def check_paragraph(text, symbol, stock_name):
    soup = BeautifulSoup(text, 'html.parser')
    paragraphs = soup.find_all('p')
    relevant_content = ""
    for paragraph in paragraphs:
        text = paragraph.get_text()
        if symbol in text or stock_name in text:
            relevant_content += text + "\n"

    return relevant_content.strip()

news = fetch_news("AAPL")
news_and_sentiment = estimate_news_sentiment(news, "AAPL", "Apple Inc.")
