import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import streamlit as st

class InvestmentsPlots:
    def __init__(self, df):
        self.df = df

    def plot_single_chart_streamlit(self, title):
        line_trace = go.Scatter(
            x=self.df['Date'],
            y=self.df['Close'],
            mode='lines',
            name='Price'
        )
        layout = go.Layout(
            title=f'{title}',
        )
        fig = go.Figure(data=[line_trace], layout=layout)
        st.plotly_chart(fig, use_container_width=True)

    def plot_moving_average(self):
        price = go.Scatter(x=self.df['Date'], y=self.df['Close'], mode='lines', name='Price')
        sma_200 = go.Scatter(x=self.df['Date'], y=self.df['SMA_200'], mode='lines', name='SMA_200')
        sma_20 = go.Scatter(x=self.df['Date'], y=self.df['SMA_20'], mode='lines', name='SMA_20')
        sma_50 = go.Scatter(x=self.df['Date'], y=self.df['SMA_50'], mode='lines', name='SMA_50')
        layout = go.Layout(
            title=f'Moving average',
        )
        fig = go.Figure(data=[price, sma_200, sma_20, sma_50], layout=layout)
        st.plotly_chart(fig, use_container_width=True)

    def plot_macd(self):
        macd = go.Scatter(x=self.df['Date'], y=self.df['MACD_12_26_9'], mode='lines', name='MACD')
        macd_signal = go.Scatter(x=self.df['Date'], y=self.df['MACDs_12_26_9'], mode='lines', name='MACD Signal')
        macd_h = go.Bar(x=self.df['Date'], y=self.df['MACDh_12_26_9'], name='MACDh')
        layout = go.Layout(
            title=f'MACD',
        )
        fig = go.Figure(data=[macd, macd_signal, macd_h], layout=layout)
        st.plotly_chart(fig, use_container_width=True)

    def plot_rsi(self):
        rsi = go.Scatter(x=self.df['Date'], y=self.df['RSI_14'], mode='lines', name='RSI_14')
        layout = go.Layout(
            title=f'RSI',
        )
        fig = go.Figure(data=[rsi], layout=layout)
        fig.add_shape(
            type="line",
            x0=self.df['Date'].min(),
            x1=self.df['Date'].max(),
            y0=70,
            y1=70,
            line=dict(color="red", width=2, dash="dash"),
        )

        fig.add_shape(
            type="line",
            x0=self.df['Date'].min(),
            x1=self.df['Date'].max(),
            y0=30,
            y1=30,
            line=dict(color="red", width=2, dash="dash"),
        )
        st.plotly_chart(fig, use_container_width=True)

    def plot_multiple_chart_streamlit(self):
        # Create subplot with two plots (1 row, 2 columns)
        fig = sp.make_subplots(rows=5, cols=1, shared_xaxes=True, subplot_titles=['Price', 'MACD', 'RSI'])

        # Trace 1
        fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['Close'], mode='lines', name='Price'), row=1, col=1)
        fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['SMA_200'], mode='lines', name='SMA_200'), row=1,
                      col=1)
        fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['SMA_20'], mode='lines', name='SMA_20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['SMA_50'], mode='lines', name='SMA_50'), row=1, col=1)

        # Trace 2
        fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['MACD_12_26_9'], mode='lines', name='MACD'), row=2,
                      col=1)
        # fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['MACDh_12_26_9'], mode='lines', name='MACDh'), row=2, col=1)
        fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['MACDs_12_26_9'], mode='lines', name='MACD Signal'),
                      row=2, col=1)
        fig.add_trace(go.Bar(x=self.df['Date'], y=self.df['MACDh_12_26_9'], name='MACDh'), row=2, col=1)

        # Trace 3
        fig.add_trace(go.Scatter(x=self.df['Date'], y=self.df['RSI_14'], mode='lines', name='RSI_14'), row=3, col=1)
        fig.add_shape(
            type="line",
            x0=self.df['Date'].min(),
            x1=self.df['Date'].max(),
            y0=70,
            y1=70,
            line=dict(color="red", width=2, dash="dash"),
            row=3,
            col=1,
        )

        fig.add_shape(
            type="line",
            x0=self.df['Date'].min(),
            x1=self.df['Date'].max(),
            y0=30,
            y1=30,
            line=dict(color="red", width=2, dash="dash"),
            row=3,
            col=1,
        )
        fig.update_layout(height=1500, width=1700)
        st.plotly_chart(fig, use_container_width=False)
