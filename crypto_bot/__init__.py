# crypto_bot/__init__.py

from typing import Any


market_data = {}
"""
Global data dictionary that stores the data from the exchanges.


exchange: binance, etc.
symbol: BTCUSDT, ETHUSDT, etc.
market_type: spot, um
event_type: bookTicker, aggTrade, markPrice, kline__1m, etc.


The data is stored in the following format:
{
    exchange: {
        symbol: {
            market_type: {
                event_type: {
                    data
                }
            }
        }
    }
}

Example:
{
    "binance": {
        "BTCUSDT": {
            "um": {
                "bookTicker": {
                    "u": 123456789,
                    "s": "BTCUSDT",
                    "b": "123.45",
                    "B": "123.45",
                    "a": "123.45",
                    "A": "123.45"
                }
            }
        }
    },
}
"""

def update_market_data(
    exchange: str,
    symbol: str,
    market_type: str,
    event_type: str,
    data: Any,      
):
    """
    Update the market data with the given data.
    
    Args:
        exchange (str): The exchange of the data.
        symbol (str): The symbol of the data.
        market_type (str): The market type of the data.
        event_type (str): The event type of the data.
        data (Any): The data to be updated.
    """
    global market_data
    try:
        market_data[exchange][symbol][market_type][event_type] = data
    except KeyError:
        if exchange not in market_data:
            market_data[exchange] = {}
        if symbol not in market_data[exchange]:
            market_data[exchange][symbol] = {}
        if market_type not in market_data[exchange][symbol]:
            market_data[exchange][symbol][market_type] = {}
        if event_type not in market_data[exchange][symbol][market_type]:
            market_data[exchange][symbol][market_type][event_type] = {}
        market_data[exchange][symbol][market_type][event_type] = data


