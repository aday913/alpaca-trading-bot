import logging
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetAssetsRequest
from alpaca.trading.enums import TimeInForce, AssetClass, AssetStatus, AssetExchange
from dotenv import load_dotenv

log = logging.getLogger(__name__)


class Broker:
    """
    Parent class for all trading brokers
    """

    def __init__(
        self, api_key: str, api_secret: str, dry_run: bool = False, paper: bool = False
    ):
        """
        Initialize the broker
        """
        if paper:
            self.client = TradingClient(
                api_key=api_key, secret_key=api_secret, paper=True
            )
        else:
            self.client = TradingClient(api_key=api_key, secret_key=api_secret)
        self.dry_run = dry_run

    def trade(
        self, symbol: str, qty: int, side: str, time_in_force: TimeInForce
    ) -> bool:
        """
        Make a trade

        :param symbol: Ticker symbol
        :param qty: Quantity
        :param side: Buy or sell
        :param time_in_force: Day or GTC
        :return: True if successful, False otherwise
        """
        log.info(f"Making trade: {side} {qty} {symbol} ({time_in_force})")
        market_order = MarketOrderRequest(
            symbol=symbol, qty=qty, side=side, time_in_force=time_in_force
        )

        try:
            if self.dry_run:
                log.info("Dry run enabled, not making trade")
                return True
            response = self.client.submit_order(order_data=market_order)
        except Exception as e:
            log.error(f"Failed to make trade: {e}")
            return False

        log.info(f"Trade made: {response}")
        return True

    def search_for_assets(self):
        """
        Search for assets available for trading

        :return: List of assets
        """
        search_params = GetAssetsRequest(
            asset_class=AssetClass.US_EQUITY,
            status=AssetStatus.ACTIVE,
            exchange=AssetExchange.NASDAQ,
        )

        try:
            assets = self.client.get_all_assets(search_params)
        except Exception as e:
            log.error(f"Failed to search for assets: {e}")
            return []

        log.info(f"Found {len(assets)} assets")
        return assets


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

    broker = Broker(
        api_key=api_key,
        api_secret=api_secret,
        dry_run=True,
        paper=True,
    )

    broker.trade(
        symbol="AAPL",
        qty=1,
        side="buy",
        time_in_force=TimeInForce.DAY,
    )

    assets = broker.search_for_assets()
    log.info(
        f"First 5 assets: {', '.join([f'{asset.symbol}: {asset.name}' for asset in assets[:5]])}"
    )
