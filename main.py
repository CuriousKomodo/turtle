import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from stocks_info import get_stock_table_with_formatting

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)
current_dir = os.path.dirname(os.path.abspath(__file__))
columns_for_index = ['Gross Profit', 'Price', 'Volume', 'Profitability', 'Volatility', 'Stability', 'Growth', 'Management', 'R&D/Gross Profit']


@app.get('/')
def welcome():
    return 'welcome turtle <3 '


@app.get("/stocks")  # TODO: This might be asynchronous in the future.
async def get_stock_table(request: Request):
    list_of_existing_stocks = ["WAFU", "EEIQ", "GME", "OCG", "KUKE", "XERIS", "BNGO", "MOMO",
                               "CODX",
                               "BOXL", "BLNK", "HOME", "MBII", "VNET", "APTO", "WGO", "SHIP", "KBH",
                               "NAVB", "APTX", "LIQT", "CLEU", "FEDU",
                               "MX"]

    stock_table = get_stock_table_with_formatting(list_of_existing_stocks)
    return templates.TemplateResponse('stocks.html',
                                      context={'request': request,
                                               'stock_table': stock_table,
                                               'columns_for_index': columns_for_index,
                                               })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
