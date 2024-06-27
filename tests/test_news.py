from models.news import NewsFromTicker
from datetime import datetime, date
import os
from dotenv import load_dotenv
import unittest

load_dotenv()
class TestNews(unittest.TestCase):
    def setUp(self):
        self.ticker = 'Ibovespa'
    def test_newsapi(self):
        api_key = os.getenv('newsapi_key')
        get_news = NewsFromTicker(self.ticker)
        df_news = get_news.newsapi(api_key)
        self.assertFalse(df_news.empty)
    def test_google_news(self):
        get_news = NewsFromTicker(self.ticker)
        df_news = get_news.googlenews()
        self.assertFalse(df_news.empty)

if __name__ == '__main__':
    unittest.main()
