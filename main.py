import os

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from stocks_info import get_stock_table_with_formatting

app = FastAPI()
templates = Jinja2Templates(directory="templates/")
current_dir = os.path.dirname(os.path.abspath(__file__))
columns_for_index = []

@app.get('/')
def welcome():
    return 'welcome turtle'

@app.get("/stocks")
def get_stock_table(request: Request):
    stock_table = get_stock_table_with_formatting()
    return templates.TemplateResponse('stocks.html',
                                      context={'request': request,
                                               'stock_table': stock_table,
                                               'columns_for_index': columns_for_index,
                                               })

