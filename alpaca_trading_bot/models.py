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


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Load API keys from .env file
    load_dotenv()
  
    model = Model()
    logging.info(f"Prediction: {model.predict()}")
