import os
import time
from concurrent.futures.process import ProcessPoolExecutor
from multiprocessing import Pool
from pathlib import Path
from typing import Dict
from uuid import UUID, uuid4
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.staticfiles import StaticFiles

from stocks_info import format_stock_table, get_all_stock_info, get_all_stocks_table_from_list


class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    status: str = "in_progress"
    result: int = None


app = FastAPI()
jobs: Dict[UUID, Job] = {}
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

@app.get("/test")
async def test_endpoint(request: Request):
    print(f"main process: {os.getpid()}")

    list_of_existing_stocks = ["WAFU", "EEIQ", "GME", "OCG", "KUKE", "XERIS", "BNGO", "MOMO",
                               "CODX",
                               "BOXL", "BLNK", "HOME", "MBII", "VNET", "APTO", "WGO", "SHIP", "KBH",
                               "NAVB", "APTX", "LIQT", "CLEU", "FEDU",
                               "MX"]
    pool = ProcessPoolExecutor(max_workers=5)
    futures = []

    for stock in list_of_existing_stocks:
        futures.append(pool.submit(get_all_stock_info,stock),)

    results = []
    for fut in futures:
        results.append(fut.result())

    # terminate the entire pool
    pool.shutdown(wait=True)

    d = {i: result for i, result in enumerate(results)}
    stock_table = get_all_stocks_table_from_list(d)
    stock_table = format_stock_table(stock_table)

    return templates.TemplateResponse('stocks.html',
                                      context={'request': request,
                                               'stock_table': stock_table,
                                               'columns_for_index': columns_for_index,
                                               })


# @app.get("/stocks")  # TODO: This might be asynchronous in the future.
# async def get_stock_table(request: Request):
#     list_of_existing_stocks = ["WAFU", "EEIQ", "GME", "OCG", "KUKE", "XERIS", "BNGO", "MOMO",
#                                "CODX",
#                                "BOXL", "BLNK", "HOME", "MBII", "VNET", "APTO", "WGO", "SHIP", "KBH",
#                                "NAVB", "APTX", "LIQT", "CLEU", "FEDU",
#                                "MX"]
#
#     stock_table = format_stock_table(list_of_existing_stocks)
#     return templates.TemplateResponse('stocks.html',
#                                       context={'request': request,
#                                                'stock_table': stock_table,
#                                                'columns_for_index': columns_for_index,
#                                                })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
