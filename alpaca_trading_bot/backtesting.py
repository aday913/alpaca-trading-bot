import datetime
import logging

from alpaca.data.timeframe import TimeFrame
from collections import defaultdict
import pandas as pd

from historical_data import HistoricalData
from models import Model

log = logging.getLogger(__name__)


class BackTester:
    def __init__(
        self,
        starting_money: float,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        symbols: list,
        strategy: Model,
        api_key: str,
        api_secret: str,
    ):
        """
        Initialize the BackTester

        :param starting_money: Starting cash amount
        :param start_date: Start date for backtest
        :param end_date: End date for backtest
        :param symbols: List of stock symbols to backtest
        :param strategy: Trading strategy (Model)
        :param api_key: Alpaca API key
        :param api_secret: Alpaca API secret
        """
        log.info("Initializing BackTester with the following parameters:")

        self.starting_money = starting_money
        log.info(f"  Starting Money: ${starting_money:.2f}")

        self.start_date = start_date
        log.info(f"  Start Date: {start_date}")

        self.end_date = end_date
        log.info(f"  End Date: {end_date}")

        self.symbols = symbols
        log.info(f"  Symbols: {symbols}")

        self.strategy = strategy
        self.historical_data = HistoricalData(api_key, api_secret)
        self.portfolio = defaultdict(lambda: {"shares": 0, "cash": 0})
        self.spy_portfolio = {"cash": starting_money, "shares": 0}
        self.results = {"strategy_value": [], "spy_value": []}

    def run(self):
        """
        Run the backtest
        """
        # Distribute starting money evenly among stocks
        cash_per_stock = self.starting_money / len(self.symbols)
        self.portfolio = {
            symbol: {"shares": 0, "cash": cash_per_stock} for symbol in self.symbols
        }
        log.info(f"Initial Portfolio: {self.portfolio}")

        # Get data for the entire period for all symbols
        data = self.historical_data.get_data(
            symbols=self.symbols,
            start=self.start_date,
            end=self.end_date,
            timeframe=TimeFrame.Day,
        )
        log.debug(f"Data: \n{data.head()}\n")
        if data.empty:
            raise ValueError("No data found")

        # Convert date range to UTC
        date_range = pd.date_range(
            self.start_date, self.end_date, freq="B"
        ).tz_localize("UTC")

        # Get SPY data for the whole period once at the beginning
        spy_data = self.historical_data.get_data(
            ["SPY"], self.start_date, self.end_date, TimeFrame.Day
        )

        # Track SPY investment (Buy once at the beginning and hold)
        initial_spy_close = None
        i = 0
        while initial_spy_close is None and i < len(spy_data):
            try:
                initial_spy_close = spy_data.loc[
                    ("SPY", date_range[i].replace(hour=5))
                ]["close"]
            except Exception:
                i += 1
                if i == len(spy_data):
                    raise ValueError("No SPY data found")
        self.spy_portfolio["shares"] = self.spy_portfolio["cash"] // initial_spy_close
        self.spy_portfolio["cash"] -= self.spy_portfolio["shares"] * initial_spy_close

        # Run the backtest
        for date in date_range:
            date = date.replace(hour=5, minute=0, second=0, microsecond=0)
            for symbol in self.symbols:
                if (symbol, date) not in data.index:
                    continue  # Skip days with no trading data for this symbol

                stock_data = data.loc[(symbol, date)]

                # Get prediction from the strategy
                decision = self.strategy.predict(data.loc[symbol])

                # Buy
                if decision == 1 and self.portfolio[symbol]["cash"] > 0:
                    price = stock_data["close"]
                    shares_to_buy = self.portfolio[symbol]["cash"] // price
                    self.portfolio[symbol]["shares"] += shares_to_buy
                    self.portfolio[symbol]["cash"] -= shares_to_buy * price
                # Sell
                elif decision == -1 and self.portfolio[symbol]["shares"] > 0:
                    price = stock_data["close"]
                    self.portfolio[symbol]["cash"] += (
                        self.portfolio[symbol]["shares"] * price
                    )
                    self.portfolio[symbol]["shares"] = 0

                # Calculate current portfolio values
                strategy_value = sum(
                    self.portfolio[symbol]["shares"] * data.loc[(symbol, date)]["close"]
                    for symbol in self.symbols
                    if (symbol, date) in data.index
                ) + sum(self.portfolio[symbol]["cash"] for symbol in self.symbols)

                spy_value = (
                    self.spy_portfolio["shares"] * spy_data.loc[("SPY", date)]["close"]
                    + self.spy_portfolio["cash"]
                )

                self.results["strategy_value"].append(strategy_value)
                self.results["spy_value"].append(spy_value)
                log.debug(f"Portfolio Value on {date}: ${strategy_value:.2f}")
                log.debug(f"SPY Portfolio Value on {date}: ${spy_value:.2f}")

        self._report()

    def _report(self):
        """
        Report the results of the backtest
        """
        initial_value = self.starting_money
        final_value = self.results["strategy_value"][-1]
        spy_initial_value = self.starting_money
        spy_final_value = self.results["spy_value"][-1]
        
        log.info('-'*50)
        log.info(f"Initial Portfolio Value: ${initial_value:.2f}")
        log.info(f"Final Portfolio Value: ${final_value:.2f}")
        log.info(f"Change: {(final_value - initial_value) / initial_value * 100:.2f}%")
        log.info(f"SPY Initial Value: ${spy_initial_value:.2f}")
        log.info(f"SPY Final Value: ${spy_final_value:.2f}")
        log.info(
            f"SPY Change: {(spy_final_value - spy_initial_value) / spy_initial_value * 100:.2f}%"
        )


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    from models import SimpleMovingAverage

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Load API keys from .env file
    load_dotenv()
    api_key = os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_SECRET_KEY")
    if not api_key:
        log.error("API key not found")
        exit(1)
    if not api_secret:
        log.error("API secret not found")
        exit(1)

    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 12, 31)
    symbols = ["AAPL", "MSFT", "GOOGL"]
    starting_money = 10000

    sma_strategy = SimpleMovingAverage(short_window=20, long_window=50)

    backtester = BackTester(
        starting_money, start_date, end_date, symbols, sma_strategy, api_key, api_secret
    )
    backtester.run()
