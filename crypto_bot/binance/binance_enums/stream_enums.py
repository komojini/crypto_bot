"""
Market Streams

For more information visit:
- SPOT: https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams
- FUTURES: https://binance-docs.github.io/apidocs/futures/en/#websocket-market-streams

- Combined stream events are wrapped as follows:
{"stream":"<streamName>","data":<rawPayload>}

- Single connection is valid for 24 hours.

- ws connections have 10 messages per second limit.
    - connection beyond the limit will be disconnected.
    - repeatedly disconnecting will result in IP ban.

- A single connection can subscribe to 200 streams.

---
User Data Streams

For more information visit:
- SPOT: https://binance-docs.github.io/apidocs/spot/en/#user-data-streams
- FUTURES: https://binance-docs.github.io/apidocs/futures/en/#user-data-streams

- A User data stream listenKey is valid for 60 minutes after creation.
"""

from enum import Enum

class StreamType(str, Enum):
    """
    The type of stream that is being used.
    """
    AGGREGATE_TRADE = 'aggTrade' # <symbol>@aggTrade
    # "s": "BTCUSDT",  # Symbol
    # update speed = Real-time(SPOT), 100ms(FUTURES)
    TRADE = 'trade' # <symbol>@trade
    # update speed = Real-time

    KLINE = 'kline' # <symbol>@kline_<interval>
    # intervals = 1s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1W, 1M
    MINI_TICKER = '24hrMiniTicker' # <symbol>@miniTicker, !miniTicker@arr 
    # All market update speed = 1000ms(FUTURES) or 1000ms(SPOT)
    TICKER = '24hrTicker' # <symbol>@ticker_<window_size>, !ticker_<window_size>@arr
    # Default window_size = 24h (24hTicker) <symbol>@ticker, !ticker@arr
    # window_sizes = 1h, 4h, 1d (only available for SPOT)
    # All market update speed = 1000ms
    BOOK_TICKER = 'bookTicker' # <symbol>@bookTicker (best bid/ask)
    # has no "e" field
    DEPTH = 'depth' # <symbol>@depth<levels>, <symbol>@depth<levels>@100ms
    # update speed is 1000ms or 100ms
    # has no "e" field
    # levels = 5, 10, 20
    # "e": "depthUpdate" for futures

    # Only for futures
    MARK_PRICE = 'markPriceUpdate' # <symbol>@markPrice, <symbol>@markPrice@1s
    # update speed is 3s or 1s
    # !markPrice@arr, !markPrice@arr@1s
    CONTINUOUS_KLINE = 'continuousKline' # <pair>@continuousKline<contractType>_<interval>
    # intervals = 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d
    LIQUIDATION_ORDER = 'forceOrder' # <symbol>@forceOrder, !forceOrder@arr

    ASSET_INDEX_UPDATE = 'assetIndexUpdate' # !assetIndex@arr, <assetSymbol>@assetIndex
    UNKNOW = 'UNKNOWN'


class StreamErrorType(int, Enum):
    UNKNOWN_PROPERTY = 0
    INVALID_VALUE_TYPE = 1
    INVALID_REQUEST = 2
    INVALID_JSON = 3

class StreamEventType(str, Enum):
    """
    The type of event that is being streamed.
    """
    # Aggregate Trade Streams

    # User Data Streams
    ACCOUNT_UPDATE = 'ACCOUNT_UPDATE'
    ORDER_TRADE_UPDATE = 'ORDER_TRADE_UPDATE'
    BALANCE_UPDATE = 'BALANCE_UPDATE'
    RISK_LEVEL_CHANGE = 'RISK_LEVEL_CHANGE'

    UNKNOWN = 'UNKNOWN'

