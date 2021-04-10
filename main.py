import os
import time
from concurrent.futures.process import ProcessPoolExecutor
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Optional, List
from uuid import UUID, uuid4
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse
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

@app.post("/login")
def login(username: str = Form(...)):
    url = app.url_path_for("stocks")
    response = RedirectResponse(url=url)
    return response

@app.get("/stocks")
async def test_endpoint(request: Request):
    print(f"main process: {os.getpid()}")

    list_of_existing_stocks = ["3SFB", "MMM", "3SQE", "FOLD", "ANPC", "EARS", "BTX", "BSQR", "CANF",
                               "CAH", "PRTS", "CHUC", "CHEK", "CLIS", "CMGR", "CCAP", "DQ", "TACO",
                               "ENTX", "EVOK", "EVOL", "XELA", "XONE", "FAMI", "FEDU", "FREQ", "GMDA"]
                               # "GNMK", "GST", "GSX", "IAG", "IDRA", "IDOX", "ILMN", "IVST", "JRSS",
                               # "KNB", "KOSS", "LTRPB", "LIQT", "LIZI", "MOMO", "NLSP", "NVFY", "ODT",
                               # "PDD", "QIWI", "RCMT", "RHDGF", "RETO", "RLX", "RUBY", "SCPS", "SEN",
                               # "SIGL", "SLNG", "SNDEQ", "SNDL", "SSY", "TKAT", "TAL", "TCLRY", "TZPS",
                               # "SPC", "UPC", "VCNX", "VUSA", "VIOT", "VOW", "WPG", "WVE", "XELB"]
    
    pool = ProcessPoolExecutor(max_workers=5)
    futures = []

    for stock in list_of_existing_stocks:
        futures.append(pool.submit(get_all_stock_info, stock))

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


@app.get("/stocks2")
async def test_endpoint(request: Request):
    print(f"main process: {os.getpid()}")

    list_of_existing_stocks = ["3SFB", "MMM", "3SQE", "FOLD", "ANPC", "EARS", "BTX", "BSQR", "CANF",
                               "CAH", "PRTS", "CHUC", "CHEK", "CLIS", "CMGR", "CCAP", "DQ", "TACO",
                               "ENTX", "EVOK", "EVOL", "XELA", "XONE", "FAMI", "FEDU", "FREQ",
                               "GMDA"]
    # "GNMK", "GST", "GSX", "IAG", "IDRA", "IDOX", "ILMN", "IVST", "JRSS",
    # "KNB", "KOSS", "LTRPB", "LIQT", "LIZI", "MOMO", "NLSP", "NVFY", "ODT",
    # "PDD", "QIWI", "RCMT", "RHDGF", "RETO", "RLX", "RUBY", "SCPS", "SEN",
    # "SIGL", "SLNG", "SNDEQ", "SNDL", "SSY", "TKAT", "TAL", "TCLRY", "TZPS",
    # "SPC", "UPC", "VCNX", "VUSA", "VIOT", "VOW", "WPG", "WVE", "XELB"]

    pool = Pool(processes=10)
    results = [pool.apply(get_all_stock_info, args=(x,)) for x in list_of_existing_stocks]

    d = {i: result for i, result in enumerate(results)}
    stock_table = get_all_stocks_table_from_list(d)
    stock_table = format_stock_table(stock_table)

    return templates.TemplateResponse('stocks.html',
                                      context={'request': request,
                                               'stock_table': stock_table,
                                               'columns_for_index': columns_for_index,
                                               })


@app.get("/test")
async def get_stock_table(request: Request):
    results = [get_all_stock_info('ANPC')]
    d = {i: result for i, result in enumerate(results)}
    stock_table = get_all_stocks_table_from_list(d)
    stock_table = format_stock_table(stock_table)
    return templates.TemplateResponse('stocks.html',
                                      context={'request': request,
                                               'stock_table': stock_table,
                                               'columns_for_index': columns_for_index,
                                               })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
