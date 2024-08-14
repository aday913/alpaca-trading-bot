import datetime
import logging
import os

from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv
import pandas as pd

log = logging.getLogger(__name__)


class HistoricalData:
    def __init__(self, api_key: str, api_secret: str):
        self.client = StockHistoricalDataClient(api_key=api_key, secret_key=api_secret)

    def get_data(
        self,
        symbols: list,
        start: datetime.datetime,
        end: datetime.datetime,
        timeframe: TimeFrame,
    ):
        log.info(
            f"Getting historical data for {symbols} from {start} to {end} with timeframe {timeframe}"
        )
        request = StockBarsRequest(
            symbol_or_symbols=symbols, start=start, end=end, timeframe=timeframe
        )

        response = self.client.get_stock_bars(request)
        return response.df

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Load API keys from .env file
    load_dotenv()
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not api_secret:
        raise ValueError("API key and secret are required")
    
    # Set up the historical data client
    hd = HistoricalData(api_key=api_key, api_secret=api_secret)

    # Configure the request
    start = datetime.datetime(2021, 1, 1)
    end = datetime.datetime(2021, 1, 31)
    timeframe = TimeFrame.Day
    
    # Get the data
    data = hd.get_data(["AAPL"], start, end, timeframe)
    
    # Print the data
    log.info(data.head())
