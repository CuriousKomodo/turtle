import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from stocks_info import get_stock_table_with_formatting

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/../static", StaticFiles(directory="static"), name="static")
current_dir = os.path.dirname(os.path.abspath(__file__))
columns_for_index = ['Gross Profit','Price', 'Profitability', 'Volatility', 'Stability', 'Growth', 'Management', 'R&D as % to Gross Profit']


@app.get('/')
def welcome():
    return 'welcome turtle <3 '

@app.get("/stocks")
def get_stock_table(request: Request):
    stock_table = get_stock_table_with_formatting()
    return templates.TemplateResponse('stocks.html',
                                      context={'request': request,
                                               'stock_table': stock_table,
                                               'columns_for_index': columns_for_index,
                                               })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)