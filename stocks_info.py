# -*- coding: utf-8 -*-
"""turtle_trading.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gBijPUM3tvZaRQ86k5sZ4l5OXX2K61e2
"""
import numpy as np
import pandas as pd
import yfinance as yf


"""# Get the list of stocks in the spreadsheet"""
list_of_metrics_to_display = []
list_of_existing_stocks = ["WAFU", "EEIQ", "GME", "OCG", "KUKE", "XERIS", "BNGO", "MOMO", "CODX",
                           "BOXL", "BLNK", "HOME", "MBII", "VNET", "APTO", "WGO", "SHIP", "KBH",
                           "NAVB", "APTX", "LIQT", "CLEU", "FEDU",
                           "MX"]  # INSERT STOCKS THAT YOU ARE INTERESTED HERE

def obtain_benchmark():
    data = {}
    return data


def get_gross_profit_data(ticker_data):
    gross_profit = None
    gross_profit_prev = None
    try:
        gross_profit = ticker_data.get_financials().loc['Gross Profit'][0]
    except IndexError:
        print('No current gross profit data')

    try:
        gross_profit_prev = ticker_data.get_financials().loc['Gross Profit'][1]
    except IndexError:
        print('No previous gross profit data')

    gross_profit_colour = 'N/A'
    if all([gross_profit, gross_profit_prev]):
        gross_profit_colour = 'green' if gross_profit > gross_profit_prev else 'red'

    return gross_profit, gross_profit_prev, gross_profit_colour


def get_other_fundamental_data(ticker_data, gross_profit):
    management = 0
    r_and_d_as_pct_to_gross_profit = 0

    # TODO: check with the year too?
    revenue = ticker_data.get_financials().loc['Total Revenue'][0]
    expense = ticker_data.get_financials().loc['Total Operating Expenses'][0]
    r_and_d = ticker_data.get_financials().loc['Research Development'][0]

    # Management
    if all([revenue, expense]):
        management = (revenue - expense)*100/expense

    # R&D ratio
    if all([gross_profit, r_and_d]):
        r_and_d_as_pct_to_gross_profit = r_and_d*100/gross_profit

    revenue = revenue if revenue else 0
    expense = expense if expense else 0
    r_and_d = r_and_d if r_and_d else 0
    return revenue, expense, r_and_d, management, r_and_d_as_pct_to_gross_profit


def get_all_stock_info(stock: str):
    ticker_data = yf.Ticker(stock)
    data = {}

    try:
        # Fundamental financial data
        market_cap = ticker_data.info['marketCap']
        gross_profit, gross_profit_prev, gross_profit_colour = get_gross_profit_data(ticker_data)
        revenue, expense, r_and_d, management, r_and_d_as_pct_to_gross_profit = get_other_fundamental_data(ticker_data, gross_profit)

        # Technical data
        ave_vol_10_days = ticker_data.info['averageVolume10days']
        ave_vol_24_hr = ticker_data.info['averageVolume']

        # historical data
        his = ticker_data.history(period="1wk", interval="5m")
        current_vol = his.iloc[-1]['Volume']
        current_price = his.iloc[-1]['Close']
        prev_vol = his.iloc[-2]['Volume']
        prev_price = his.iloc[-2]['Close']

        price_colour = 'N/A'
        volume_colour = 'N/A'
        if all([current_price, prev_price]):
            price_colour = 'green' if current_price > prev_price else 'red'
        if all([current_vol, prev_vol]):
            volume_colour = 'green' if current_vol > prev_vol else 'red'

        market_size = ave_vol_24_hr * current_price

        profit = None
        if gross_profit:
            profit = gross_profit/market_size - 1

        # Volatility
        volatility = None
        if prev_vol>0:
            volatility = (current_vol - prev_vol)/prev_vol

        # Stability
        stability = None
        if ave_vol_10_days:
            stability = (ave_vol_24_hr - ave_vol_10_days)/ave_vol_10_days  # TODO: calcualte fotr 30 days insteds

        # Growth
        growth = None
        if market_size:
            growth = (market_cap - market_size)/market_size  # TODO: market size based 5min.

        data = {'Symbol': stock,
                'Gross Profit': gross_profit,
                'Prev Gross Profit': np.round(gross_profit_prev, 2),
                'Market Cap': float(np.round(market_cap, -3)),
                'Market Size': np.round(market_size, -3),
                'Profitability': int(profit),
                'Price': np.round(current_price, 2),
                'Prev Price': np.round(prev_price, 2),
                'Volume': float(current_vol),
                'Prev Volume': float(prev_vol),
                'Daily Average Volume': float(np.round(ave_vol_24_hr, 2)),
                'Average Volume 10 days': float(np.round(ave_vol_10_days, 2)),
                'Total Revenue': float(np.round(revenue, 2)),
                'Total Expense': float(np.round(expense, 2)),
                'Volatility': float(np.round(volatility)),
                'Stability': float(np.round(stability)),
                'Growth': float(np.round(growth)),
                'Management': float(np.round(management)),
                'R&D/Gross Profit': float(np.round(r_and_d_as_pct_to_gross_profit)),
                'Volume Color': volume_colour,
                'Price Color': price_colour,
                'Gross Profit Color': gross_profit_colour,
                }

    except Exception:
        print('Cannot retrieve data for : {}'.format(stock))

    return data


def get_all_stocks_table_from_list(list_of_stock_dict):
    pd.set_option('display.float_format',
                  lambda x: '%.3f' % x)  # to display without scientific format
    pd.options.display.float_format = '{:,}'.format
    df = pd.DataFrame.from_dict(list_of_stock_dict, "index")
    return df


def format_stock_table(stock_table):
    currency_columns = ['Gross Profit', 'Prev Gross Profit', 'Market Cap', 'Market Size',
                        'Total Revenue', 'Total Expense']
    price_columns = ['Price', 'Prev Price']
    int_columns = ['Volume', 'Average Volume 10 days', 'Prev Volume']
    percentage_columns = ['Stability', 'Profitability', 'Volatility', 'Growth', 'Management', 'R&D/Gross Profit']

    stock_table[percentage_columns].style.format('{:,.2f}%')
    stock_table[int_columns].style.format('{:,.0f}')

    for col_name in currency_columns:
        stock_table[col_name] = stock_table[col_name].map('${:,.0f}'.format)

    for col_name in price_columns:
        stock_table[col_name] = stock_table[col_name].map('${:,.2f}'.format)

    stock_table.replace([np.inf, -np.inf], 'N/A', inplace=True)
    return stock_table


"""## Display Table - might take 5min to generate all the stock information"""
if __name__ == "__main__":
    format_stock_table(list_of_existing_stocks[:2])
