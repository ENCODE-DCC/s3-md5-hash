from datetime import datetime
from random import randint
from typing import TYPE_CHECKING, Any, Dict
from uuid import uuid4

if TYPE_CHECKING:
    from aws_lambda_typing import Context


def lambda_handler(event: Dict[str, Any], context: Context) -> Dict[str, Any]:
    """Sample Lambda function which mocks the operation of selling a random number
    of shares for a stock.

    For demonstration purposes, this Lambda function does not actually perform any
    actual transactions. It simply returns a mocked result.

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        dict: Object containing details of the stock selling transaction
    """
    # Get the price of the stock provided as input
    stock_price = event["stock_price"]
    # Mocked result of a stock selling transaction
    transaction_result = {
        "id": str(uuid4()),  # Unique ID for the transaction
        "price": str(stock_price),  # Price of each share
        "type": "sell",  # Type of transaction (buy/sell)
        # Number of shares bought/sold
        # We are mocking this as a random integer between 1 and 10)
        "qty": str(randint(1, 10)),
        # Timestamp of the when the transaction was completed
        "timestamp": datetime.now().isoformat(),
    }
    return transaction_result
