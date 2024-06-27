from dotenv import load_dotenv
from newsapi import NewsApiClient
from dateutil.relativedelta import relativedelta
import re
import os
from datetime import datetime, date
import pandas as pd
from app.utils import companies
from GoogleNews import GoogleNews

load_dotenv()
api_key = os.getenv('newsapi_key')

class NewsFromTicker:
    def __init__(self, ticker):
        self.current_date = datetime.now().date()
        self.one_month_before = datetime.now() - relativedelta(months=1)
        self.ticker = ticker
    def newsapi(self, api_key):
        # NEWS
        newsapi = NewsApiClient(api_key=api_key)
        # Get the current date
        # current_date = datetime.now()
        # # Get the date one month before the current date
        # one_month_before = current_date - relativedelta(months=1)

        all_articles = newsapi.get_everything(
            q=f'{self.ticker}',
            from_param=self.one_month_before,
            to=self.current_date,
            language='pt',
            sort_by='relevancy',
        )

        df_news = pd.DataFrame(all_articles['articles'])
        if df_news.empty:
            all_articles = newsapi.get_everything(
                q=f'Ibovespa',
                from_param=self.one_month_before,
                to=self.current_date,
                language='pt',
                sort_by='relevancy',
            )
            df_news = pd.DataFrame(all_articles['articles'])

        # Removendo a Timezone da coluna de publicação
        df_news['publishedAt'] = df_news['publishedAt'].apply(lambda x: re.sub("[a-zA-Z]+", '', x))

        # Colocando espaçamento entre data e hora e transfornmando a coluna de publicação em formato de data
        df_news['publishedAt'] = df_news['publishedAt'].apply(
            lambda x: datetime.strptime(x[2:10] + ' ' + x[10:], '%y-%m-%d %H:%M:%S'))

        # Pegando apenas o nome da fonte
        df_news['source'] = df_news['source'].apply(lambda x: x['name'])

        # Removendo colunas desnecessárias
        df_news.drop(columns=['author', 'urlToImage'], inplace=True)
        df_news = df_news.sort_values(by='publishedAt', ascending=False).reset_index(drop=True)
        df_news.columns = ['publisher','title','description','url','publishedAt','content']

        return df_news

    def googlenews(self):
        start_dt = self.one_month_before
        end_dt = self.current_date
        googlenews= GoogleNews(start=self.one_month_before,
                   end=self.current_date)
        googlenews.setlang('pt')
        googlenews.search(self.ticker)
        df_google_news = pd.DataFrame(googlenews.result())

        if df_google_news.empty:
            googlenews = GoogleNews(start=start_dt.strftime('%Y-%m-%d'),
                                    end=end_dt.strftime('%Y-%m-%d'))
            googlenews.setlang('pt')
            googlenews.search('Ibovespa')
            df_google_news = pd.DataFrame(googlenews.result())

        df_google_news.drop(columns=['img'], inplace=True)
        #df_google_news = df_google_news.sort_values(by='date')
        df_google_news.columns = ['title','publisher','publishedAt','datetime','description','url']
        df_google_news = df_google_news[['publisher','title','description','url','publishedAt','datetime']]

        return df_google_news
