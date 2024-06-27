from app.utils import MyStrategy, stock_list, companies
import streamlit as st
import pandas_ta as ta
from datetime import datetime, date
import pandas as pd
import os
from dotenv import load_dotenv
from models.news import NewsFromTicker
from models.plots import InvestmentsPlots
from models.strategies import *

load_dotenv()
api_key = os.getenv('newsapi_key')

def get_historical_stock_data(ticker, MyStrategy, begin_dt, end_dt):
    df = pd.DataFrame()
    df = df.ta.ticker(ticker)
    df.ta.strategy(MyStrategy)
    df = df.reset_index()

    df_filter = df[(df['Date'].dt.date >= begin_dt) & (df['Date'].dt.date <= end_dt)].reset_index()
    return df_filter


def get_historical_stock_price(ticker):
    df = yf.download(ticker, period="max")
    df = df.reset_index()
    df['daily_return'] = round(df['Close'].pct_change() * 100, 2)

    # Get current date
    current_date = datetime.now().date()
    # Get the date one year before
    one_year_before = current_date.replace(year=current_date.year - 1).strftime("%Y-%m-%d")
    # Get the first day of the year
    first_day_of_year = current_date.replace(month=1, day=1).strftime("%Y-%m-%d")

    # Calculate the returns
    current_value = df['Close'].values[-1]
    # 1 year return
    one_year_value = df[df['Date'] >= one_year_before]['Close'].values[0]
    one_year_return = round(((current_value / one_year_value) - 1) * 100, 2)
    # Year-to-Date (YTD) return
    ytd_return = df[df['Date'] >= first_day_of_year]['Close'].values[0]
    ytd_return = round(((current_value / ytd_return) - 1) * 100, 2)

    df = df[(df['Date'].dt.date >= begin_dt) & (df['Date'].dt.date <= end_dt)].reset_index()

    results = {
        'daily_return': df['daily_return'].values[-1],
        'one_year_return': one_year_return,
        'ytd_return': ytd_return,
    }
    return df, results

# Function to generate colored HTML text
def colored_html(value):
    if value == 'Buy':
        color = "green"
    elif value == 'Sell':
        color = "red"
    else:
        color = 'grey'
    return f"<span style='color:{color}'>{value}</span>"

def streamlit_container(title, value, hight=200, border=True):
    with st.container(border=border, height=hight):
        st.markdown(f'''
        <center><b>{title}</b></center>

        ---
        <center>{value}<center>
        ''', unsafe_allow_html=True)
def get_signal_from_strategy(positive_signal, negative_signal):
    if positive_signal:
        return 'Buy'
    elif negative_signal:
        return 'Sell'
    else:
        return 'Neutral'


if __name__ == '__main__':

    # INTRODUCTION
    st.set_page_config(page_title="Plotting Demo", page_icon="📈")
    st.title('Investiment Analysis')
    st.markdown('''
     This is your all-in-one web app for comprehensive investment analysis. Designed for both novice and seasoned 
     investors, our platform provides real-time data, in-depth market insights, and the latest financial news to help 
     you make informed investment decisions.
     
     <hr style="border: none; height: 2px; background-color: red;">
    ''',
        unsafe_allow_html=True)

    # SETTINGS
    # choosing the stock
    tickers = [i + '.SA' for i in stock_list]
    tickers = tuple(['^BVSP'] + tickers)

    with st.sidebar:
        option = st.selectbox("Ticker", tickers)
        year_ref = datetime.now().year
        begin_dt = st.date_input("Begin date", date(year_ref, 1, 1))
        end_dt = st.date_input("End date", datetime.now().date())

    # NEWS
    # Determine the number of columns based on the size of the DataFrame
    company_name = companies[option][0]
    get_news = NewsFromTicker(company_name)

    with st.sidebar:
        select_source = st.selectbox(
            "News source",
            ("Google News", "News API")
        )
    df_news = get_news.newsapi(api_key) if select_source == 'News API' else get_news.googlenews()
    df_news = df_news[df_news['title'].notna()]
    source_list = list(df_news['publisher'].unique())

    with st.sidebar:
        select_publisher = st.multiselect(
            "Publisher",
            source_list
        )
    select_publisher = select_publisher if len(select_publisher) > 0 else source_list
    df_news_filter = df_news[df_news['publisher'].isin(select_publisher)]

    num_columns = len(df_news_filter.head(5))
    # Create the columns
    columns = st.columns(num_columns)

    # Populate the columns with data from the DataFrame
    for index, column in enumerate(columns):
        with column:
            st.markdown(f'''
                        **{df_news_filter.iloc[index, 1]}**
                        ''')
            st.markdown(f'''
            {df_news_filter.iloc[index, 2]}  
            Publisher: [{df_news_filter.iloc[index, 0]}]({df_news_filter.iloc[index, 3]})  
            ''')
    st.divider()

    # PLOTS
    #Get data
    ibovespa_technical = get_historical_stock_data(option, MyStrategy, begin_dt, end_dt)
    ticker_prices_data, ticker_returns = get_historical_stock_price(option)

    investment_plots_technical = InvestmentsPlots(ibovespa_technical)
    price_plot = InvestmentsPlots(ticker_prices_data)

    # Calculating returns
    year_return = ticker_returns['one_year_return']
    daily_return = ticker_returns['daily_return']
    ytd_return = ticker_returns['ytd_return']

    current_date = datetime.now().date()
    current_date = current_date.replace(year=current_date.year - 1)
    current_date = current_date.strftime("%Y-%m-%d")

    current_price = round(ticker_prices_data['Close'].iloc[-1], 2)

    col1, col2 = st.columns([4, 1])  # col1 will be twice as wide as col2 and col3

    with col1:
        with st.container(height=420, border=True):
            price_plot.plot_single_chart_streamlit(company_name)

    with col2:
        col21, col22 = st.columns(2)
        with col21:
            streamlit_container(title='Current Price (R$)', value=current_price, hight=200, border=True)
            streamlit_container(title='12m return (%)', value=year_return, hight=200, border=True)
        with col22:
            streamlit_container(title='Daily return (%)', value=daily_return, hight=200, border=True)
            streamlit_container(title='YTD return (%)', value=ytd_return, hight=200, border=True)

    st.header('Technical Analysis')
    st.divider()

    # Get signals
    if option != '^BVSP':
        st.subheader('Technical Indicators Strategies')
        daily_update = pd.read_csv('C:\\Users\\arthu\\PycharmProjects\\investment_analysis\\data\\daily_update.csv')
        # daily_update = update_all_ticker_signals(daily_update)
        best_stock_strategy = pd.read_csv(
            'C:\\Users\\arthu\\PycharmProjects\\investment_analysis\\data\\best_strategy.csv')
        daily_update = get_stock_signal(f'{companies[option][1]}', best_stock_strategy)


        strategy_rsi_70 = get_signal_from_strategy(daily_update['strategy_rsi_70'].values[0],
                                                   False)
        strategy_rsi_50 = get_signal_from_strategy(daily_update['strategy_rsi_50'].values[0],
                                                   False)
        strategy_sma_200 = get_signal_from_strategy(daily_update['strategy_sma_200'].values[0],
                                                    daily_update['neg_sma_200'].values[0])
        strategy_macd = get_signal_from_strategy(daily_update['strategy_macd'].values[0],
                                                 daily_update['neg_macd'].values[0])
        gc = get_signal_from_strategy(daily_update['GC'].values[0],
                                      daily_update['neg_GC'].values[0])
        strategy_sma_200_rsi = get_signal_from_strategy(daily_update['strategy_sma_200_rsi'].values[0],
                                                        False)
        strategy_macd_rsi_50 = get_signal_from_strategy(daily_update['strategy_macd_rsi_50'].values[0],
                                                        False)
        strategy_macd_rsi_70 = get_signal_from_strategy(daily_update['strategy_macd_rsi_70'].values[0],
                                                        False)
        strategy_macd_gc = get_signal_from_strategy(daily_update['strategy_macd_gc'].values[0],
                                                    False)
        strategy_high_trend_basic = get_signal_from_strategy(daily_update['strategy_high_trend_basic'].values[0],
                                                             False)
        strategy_high_trend_complete = get_signal_from_strategy(daily_update['strategy_high_trend_complete'].values[0],
                                                                False)
        strategy_trend_basic = get_signal_from_strategy(daily_update['strategy_trend_basic'].values[0],
                                                        False)


        st.markdown(f'''
            <div style='display: flex; flex-wrap: wrap;'>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>RSI 70</strong><br>{colored_html(strategy_rsi_70)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>RSI 50</strong><br>{colored_html(strategy_rsi_50)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>SMA 200</strong><br>{colored_html(strategy_sma_200)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>MACD</strong><br>{colored_html(strategy_macd)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>GC</strong><br>{colored_html(gc)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>SMA 200 + RSI</strong><br>{colored_html(strategy_sma_200_rsi)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>MACD + RSI 50</strong><br>{colored_html(strategy_macd_rsi_50)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>MACD + RSI 70</strong><br>{colored_html(strategy_macd_rsi_70)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>MACD + GC</strong><br>{colored_html(strategy_macd_gc)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>Positive Strategies</strong><br>{colored_html(strategy_high_trend_basic)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>High trend</strong><br>{colored_html(strategy_high_trend_complete)}
            </div>
            <div style='flex: 1 0 25%; padding: 10px;'>
                <strong>Positive force</strong><br>{colored_html(strategy_trend_basic)}
            </div>
        </div>
            ''', unsafe_allow_html=True)

    st.write('')

    tab1, tab2, tab3 = st.tabs(["Moving average", "MACD", "RSI"])

    with tab1:
        investment_plots_technical.plot_moving_average()

    with tab2:
        investment_plots_technical.plot_macd()

    with tab3:
        investment_plots_technical.plot_rsi()
