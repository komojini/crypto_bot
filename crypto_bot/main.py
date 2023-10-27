# cryptobot/main.py

import os
from datetime import datetime
from .binance.binance_client import BinanceClient
from .binance.message_handler import BinanceWSMessageHandler
from .utils.util import repeat_running_until_keyboard_interrupt
from .binance import message_handler as mh 
from . import market_data as m

um_streams = [
    "!bookTicker",
    "!markPrice@arr",
]

message_handler = BinanceWSMessageHandler(
    # callback=lambda msg: print(msg),
)
binance_client = BinanceClient(
    message_handler=message_handler
)

def fn():
    os.system("clear")
    trb_book_ticker = m["binance"]["TRBUSDT"]["um"]["bookTicker"]
    print(f"""
TRBUSDT: {trb_book_ticker["b"]},

{datetime.fromtimestamp(int(trb_book_ticker["E"])/1000)}
""")


if __name__ == "__main__":
    binance_client.start_stream(
        um_streams=um_streams,
    )

    repeat_running_until_keyboard_interrupt(
        fn=fn,
        interval=0.1,
    )

    binance_client.stop_stream()    