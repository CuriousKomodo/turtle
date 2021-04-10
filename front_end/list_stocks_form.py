from starlette_wtf import StarletteForm
from wtforms import TextField
from wtforms.validators import DataRequired

class ListStocksForm(StarletteForm):
    stocks = TextField(
        'Stocks',
        validators=[
            DataRequired('Please enter the stocks that you are interested'),
        ]
    )
