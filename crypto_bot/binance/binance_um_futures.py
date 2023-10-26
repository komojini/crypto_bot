#!/usr/bin/env python

import time
import logging
from binance.lib.utils import config_logging
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import os 
from dotenv import load_dotenv
config_logging(logging, logging.DEBUG)

load_dotenv()

def message_handler(_, message):
    print(message)


api_key, secret_key = os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_SECRET_KEY")

client = UMFutures(api_key)
response = client.new_listen_key()

logging.info("Listen key : {}".format(response["listenKey"]))

ws_client = UMFuturesWebsocketClient(on_message=message_handler)

ws_client.user_data(
    listen_key=response["listenKey"],
    id=1,
)

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break

logging.debug("closing ws connection")
ws_client.stop()