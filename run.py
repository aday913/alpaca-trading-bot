import datetime
import logging
import os

from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import TimeInForce
from dotenv import load_dotenv

from alpaca_trading_bot.broker import Broker
from alpaca_trading_bot.historical_data import HistoricalData
from alpaca_trading_bot.models import Model
from alpaca_trading_bot.utils import send_discord_message

log = logging.getLogger(__name__)


def main(
    api_key: str,
    api_secret: str,
    discord_url: str | None,
    dry_run: bool = True,
    paper: bool = True,
):
    """
    Main function for the trading bot

    :param api_key: Alpaca API key
    :param api_secret: Alpaca secret
    """
    # Initialize the broker
    broker = Broker(
        api_key=api_key, api_secret=api_secret, dry_run=dry_run, paper=paper
    )
    data_client = HistoricalData(api_key=api_key, api_secret=api_secret)
    model = Model()

    # Get historical data for apple stock
    symbols = ["AAPL"]
    start = datetime.datetime(2021, 1, 1)
    end = datetime.datetime(2021, 1, 31)
    timeframe = TimeFrame.Day
    data = data_client.get_data(
        symbols=symbols, start=start, end=end, timeframe=timeframe
    )
    log.info(f"Data: \n{data}\n")

    # Make a prediction
    prediction = model.predict()
    log.info(f"Prediction: {prediction}")

    # Make a trade
    symbol = "AAPL"
    qty = 1
    side = "buy"
    time_in_force = TimeInForce.DAY
    broker.trade(symbol=symbol, qty=qty, side=side, time_in_force=time_in_force)

    # Send a message to Discord
    if not discord_url:
        log.error("Discord URL not found, skipping message")
        return
    message = "Hello, world!"
    send_discord_message(url=discord_url, message=message)


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Load API keys from .env file
    load_dotenv()

    api_key = os.getenv("PAPER_ALPACA_API_KEY")
    api_secret = os.getenv("PAPER_ALPACA_SECRET_KEY")

    if not api_key:
        log.error("API key not found")
        exit(1)
    if not api_secret:
        log.error("API secret not found")
        exit(1)

    discord_url = os.getenv("DISCORD_WEBHOOK_URL")

    main(
        api_key=api_key,
        api_secret=api_secret,
        discord_url=discord_url,
        dry_run=True,
        paper=True,
    )
