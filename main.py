import os
import time
import requests
from concurrent.futures.process import ProcessPoolExecutor
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Optional, List
from uuid import UUID, uuid4
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from jinja2 import Template
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_302_FOUND

from front_end.list_stocks_form import ListStocksForm
from stocks_info import format_stock_table, get_all_stock_info, get_all_stocks_table_from_list
from utils.convert_string_to_list import convert_string_to_integer_list


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


@app.get('/stocks2/{list_of_stocks_str}')
async def get_stocks_table(request: Request, list_of_stocks_str: str):
    print(f"main process: {os.getpid()}")
    print(list_of_stocks_str)
    list_of_stocks = []
    try:
        list_of_stocks = convert_string_to_integer_list(list_of_stocks_str)
    except ValueError:
        print('Error: Unable to convert the following to list: {}. Remember to separate your sessions with ",", or '
                'use ":" to define range. Spacing does not matter.'.format(list_of_stocks_str))
    print(list_of_stocks)

    if list_of_stocks:
        pool = Pool(processes=5)
        results = pool.map(get_all_stock_info, list_of_stocks)
        pool.close()
        pool.join()

        d = {i: result for i, result in enumerate(results)}
        stock_table = get_all_stocks_table_from_list(d)
        stock_table = format_stock_table(stock_table)

        return templates.TemplateResponse('stocks.html',
                                          context={'request': request,
                                                   'stock_table': stock_table,
                                                   'columns_for_index': columns_for_index,
                                                   })
    else:
        print('Error')


@app.route('/choose-stocks', methods=['GET', 'POST'])
async def chose_stocks(request):
    form = await ListStocksForm.from_formdata(request)

    # validate form
    if await form.validate_on_submit():
        list_of_stocks_str = form.stocks.data
        stocks_data_url = app.url_path_for('get_stocks_table', **{"list_of_stocks_str": list_of_stocks_str})
        return RedirectResponse(stocks_data_url, status_code=HTTP_302_FOUND)

    return templates.TemplateResponse('choose_stocks.html',
                                      context={'request': request,
                                               'form': form,
                                               })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
