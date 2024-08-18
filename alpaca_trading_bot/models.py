import datetime
import logging
import os
import random

from dotenv import load_dotenv
import pandas as pd


class Model:
    """
    Parent class for all decision-making broker models
    """

    def __init__(self):
        """
        Initialize the model
        """
        pass

    def predict(self) -> int:
        """
        Make a prediction

        :return: Prediction (-1, 0, 1)
        """
        return random.randint(-1, 1)


class SimpleMovingAverage(Model):
    """
    Simple moving average model
    """

    def __init__(self, short_window: int, long_window: int):
        """
        Initialize the model

        :param short_window: Short moving average window
        :param long_window: Long moving average window
        """
        self.short_window = short_window
        self.long_window = long_window

    def predict(self, data: pd.DataFrame) -> int:
        """
        Make a prediction
        
        :param data: Data to use for prediction

        :return: Prediction (-1, 0, 1)
        """
        data = data.sort_index()

        # Calculate short and long moving averages
        data["short_mavg"] = (
            data["close"].rolling(window=self.short_window, min_periods=1).mean()
        )
        data["long_mavg"] = (
            data["close"].rolling(window=self.long_window, min_periods=1).mean()
        )

        # Get the last available short and long moving average values
        short_mavg = data["short_mavg"].iloc[-1]
        long_mavg = data["long_mavg"].iloc[-1]

        # Generate trading signal
        signal = 1 if short_mavg > long_mavg else -1

        return signal


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Load API keys from .env file
    load_dotenv()

    model = Model()
    logging.info(f"Prediction: {model.predict()}")
