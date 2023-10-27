import logging
import time
import glob
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
import os
import json
from datetime import datetime

config_logging(logging, logging.DEBUG)


def message_handler(_, message):
    message = json.loads(message)
    if "stream" in message and "data" in message:
        if message["stream"] == "stxusdt@aggTrade":
            print(message["data"])
        else:
            for ticker in message["data"]:
                
                globals()[ticker["s"]] = ticker["c"]
                globals()["_" + ticker["e"] + "__" + ticker["s"]] = ticker
my_client = SpotWebsocketStreamClient(on_message=message_handler, is_combined=True)


my_client.subscribe(
    stream=[
        "!miniTicker@arr",
        "stxusdt@aggTrade",
    ],
)

while True:
    try:
        os.system("clear")
        print(
f"""
BTCUSDT: {BTCUSDT}, {_24hrMiniTicker__BTCUSDT["q"]}
ETHUSDT: {ETHUSDT}, {_24hrMiniTicker__ETHUSDT["q"]}
BNBUSDT: {BNBUSDT}, {_24hrMiniTicker__BNBUSDT["q"]}
TRBUSDT: {TRBUSDT}, {_24hrMiniTicker__TRBUSDT["q"]}
STXUSDT: {STXUSDT}, {_24hrMiniTicker__STXUSDT["q"]}

"""
        )
        time.sleep(0.3)
    except KeyboardInterrupt:
        break
    except Exception as e:
        time.sleep(1)
        print(e)
         
my_client.stop()