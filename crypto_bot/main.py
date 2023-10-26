from .binance.binance_client import BinanceClient
from .binance.message_handler import BinanceWSMessageHandler
from .utils.util import wait_until_keyboard_interrupt

um_streams = [
    "!bookTicker",
    "!markPrice@arr",
]

message_handler = BinanceWSMessageHandler()
binance_client = BinanceClient(
    message_handler=message_handler
)

if __name__ == "__main__":
    binance_client.start_stream(
        um_streams=um_streams,
    )

    wait_until_keyboard_interrupt()

    binance_client.stop_stream()    