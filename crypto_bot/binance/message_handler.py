import json
import time
from crypto_bot import market_data, update_market_data

class BinanceWSMessageHandler:
    """
    A class that handles messages from the Binance websocket streams.
    """
    def __init__(self,
                 callback=None):
        self.handler_tree = None
        self.callback = callback

        self._initialize_handler_tree()
    

    def _initialize_handler_tree(self):
        self.handler_tree = {
            "spot": {
                "e": {
                    # Market Streams
                    "aggTrade": self._agg_trade_handler,
                    "trade": self._trade_handler,
                    "kline": self._kline_handler,
                    "24hrMiniTicker": self._miniticker_handler,
                    "24hrTicker": self._ticker_handler,
                    "1hTicker": self._window_ticker_handler,
                    "4hTicker": self._window_ticker_handler,
                    "1dTicker": self._window_ticker_handler,

                    # User Data Streams
                    "outboundAccountInfo": self._outbound_account_info_handler,
                    "balanceUpdate": self._balance_update_handler,
                    "executionReport": self._execution_report_handler, # https://binance-docs.github.io/apidocs/spot/en/#public-api-definitions
                    "depthUpdate": self._depth_handler,
                    "bookTicker": self._spot_book_ticker_handler,
                },
            },
            "um": {
                "e": {
                    # Market Streams
                    "aggTrade": self._agg_trade_handler,
                    "markPriceUpdate": self._mark_price_update_handler,
                    "kline": self._kline_handler,
                    "continuous_kline": self._continuous_kline_handler,
                    "24hrMiniTicker": self._miniticker_handler,
                    "24hrTicker": self._ticker_handler,
                    "bookTicker": self._um_book_ticker_handler,
                    "forceOrder": self._force_order_handler,
                    "depthUpdate": self._um_depth_handler,
                    "compositeIndex": self._composite_index_handler,
                    "contractInfo": self._contract_info_handler,
                    "assetIndexUpdate": self._asset_index_handler,

                    # User Data Streams
                    "MARGIN_CALL": self._um_margin_call_handler,
                    "ACCOUNT_UPDATE": self._um_account_update_handler,
                    "ORDER_TRADE_UPDATE": self._um_order_trade_update_handler,
                    "ACCOUNT_CONFIG_UPDATE": self._um_account_config_update_handler,
                    "STRATEGY_UPDATE": self._um_strategy_update_handler,
                    "GRID_UPDATE": self._um_grid_update_handler,
                    "CONDITIONAL_ORDER_TRIGGER_REJECT": self._um_conditional_order_trigger_reject_handler,
                },
            },
        }


    um_ACCOUNT_UPDATE_HANDLER_TREE = {}
    um_ORDER_TRADE_UPDATE_HANDLER_TREE = {}
    um_STRATEGY_UPDATE_HANDLER_TREE = {}

    EXECUTION_REPORT_HANDLER_TREE = {
        # See more here: https://binance-docs.github.io/apidocs/spot/en/#public-api-definitions
        
    }

    """Spot Websocket Handlers"""

    def _agg_trade_handler(self, message, market: str, **kwargs):
        """
        Aggregate trade streams push trade information that is aggregated for a single taker order.

        See more here: https://binance-docs.github.io/apidocs/futures/en/#aggregate-trade-streams
        """
        symbol = message["s"] # Symbol (e.g. "BTCUSDT")
        # price = message["p"]
        # quantity = message["q"]
        # trade_time = message["T"]
        update_market_data(
            exchange="binance",
            symbol=symbol,
            market_type=market,
            event_type="aggTrade",
            data=message,
        )

    def _trade_handler(self, message, **kwargs):
        """
        Trade streams push raw trade information; each trade has a unique buyer and seller.
        """
        symbol = message["s"] # Symbol (e.g. "BTCUSDT")
        update_market_data("binance", symbol, "spot", "trade", message)
    
    def _kline_handler(self, message, market: str, **kwargs):
        """
        Kline/candlestick Stream push updates to the current klines/candlestick every second.
        
        """
        symbol = message["s"] # Symbol (e.g. "BTCUSDT")
        interval = message["k"]["i"] # Interval (e.g. "1m")
        update_market_data("binance", symbol, market, f"kline__{interval}", message)
    
    def _ticker_handler(self, message, market: str, **kwargs):
        """
        24hr rolling window ticker statistics for a single symbol pushed every second.
        These are NOT the statistics of the UTC day, but a 24hr rolling window for the previous 24hrs.
        
        """
        symbol = message["s"]
        update_market_data("binance", symbol, market, "ticker", message)

    def _window_ticker_handler(self, message, **kwargs):
        raise NotImplementedError

    def _miniticker_handler(self, message, market: str, **kwargs):
        """
        24hr rolling window mini-ticker statistics. These are NOT the statistics of the UTC day.
        but a 24hr rolling window for the previous 24hrs.
        """
        symbol = message["s"]
        update_market_data("binance", symbol, market, "miniTicker", message)

    def _spot_book_ticker_handler(self, message, **kwargs):
        """
        Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.
        Payload:
        {
            "u":400900217,     // order book updateId
            "s":"BNBUSDT",     // symbol
            "b":"25.35190000", // best bid price
            "B":"31.21000000", // best bid qty
            "a":"25.36520000", // best ask price
            "A":"40.66000000"  // best ask qty
        }
        """
        symbol = message["s"]
        update_market_data("binance", symbol, "spot", "bookTicker", message)

    def _depth_handler(self, message, market: str, **kwargs):
        update_market_data("binance", message["s"], market, "depth", message)

    def _outbound_account_info_handler(self, message):
        raise NotImplementedError

    def _balance_update_handler(self, message):
        raise NotImplementedError

    def _execution_report_handler(self, message):
        """
        See more here: https://binance-docs.github.io/apidocs/spot/en/#public-api-definitions
        """
        raise NotImplementedError


    """UM Futures Websocket Handlers"""

    
    def _mark_price_update_handler(self, message, **kwargs):
        """
        Mark price and funding rate for a single symbol pushed every 3 or 1 seconds.
        """
        symbol = message["s"] # Symbol (e.g. "BTCUSDT")
        mark_price = message["p"] # Mark price
        funding_rate = message["r"] # Funding rate
        next_funding_time = message["T"] # Next funding time
        update_market_data("binance", symbol, "um", "markPriceUpdate", message)
        update_market_data("binance", symbol, "um", "markPrice", mark_price)
        update_market_data("binance", symbol, "um", "fundingRate", funding_rate)
        update_market_data("binance", symbol, "um", "nextFundingTime", next_funding_time)

    def _continuous_kline_handler(self, message):
        raise NotImplementedError
    
    def _force_order_handler(self, message):
        raise NotImplementedError

    def _asset_index_handler(self, message):
        raise NotImplementedError

    def _composite_index_handler(self, message):
        raise NotImplementedError 

    def _asset_index_handler(self, message):
        raise NotImplementedError

    def _contract_info_handler(self, message):
        raise NotImplementedError

    def _um_depth_handler(self, message):
        raise NotImplementedError


    def _um_book_ticker_handler(self, message, **kwargs):
        """
        Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.
        Payload:
        {
            "e": "bookTicker",  // Event type
            "u": 400900217,     // order book updateId
            "E": 1568014460893, // Event time
            "T": 1568014460891, // transaction time
            "s": "BNBUSDT",     // symbol
            "b": "25.35190000", // best bid price
            "B": "31.21000000", // best bid qty
            "a": "25.36520000", // best ask price
            "A": "40.66000000"  // best ask qty
        }

        e.g.: Binance__um__BNBUSDT__book_ticker
        """
        symbol = message["s"]
        update_market_data("binance", symbol, "um", "bookTicker", message)

    def _um_margin_call_handler(self, message):
        raise NotImplementedError

    def _um_account_update_handler(self, message):
        raise NotImplementedError

    def _um_order_trade_update_handler(self, message):
        raise NotImplementedError

    def _um_account_config_update_handler(self, message):
        raise NotImplementedError

    def _um_strategy_update_handler(self, message):
        raise NotImplementedError

    def _um_grid_update_handler(self, message):
        raise NotImplementedError

    def _um_conditional_order_trigger_reject_handler(self, message, **kwargs):
        raise NotImplementedError

    def _unknown_event_type_handler(self, message, market: str, stream_name: str, **kwargs):
        
        raise Exception(f"Unknown event type: {message}\n \
                          Market: {market}\n \
                          Stream name: {stream_name}\n \
                          Additional kwargs: {kwargs}")

    def _handle_single_data_point(self, data_point: dict, market: str, stream_name: str):
        """
        Handle a single data point.
        """
        event_type = data_point.get("e")

        if event_type:
            handler = self.handler_tree[market]["e"].get(event_type)
            if handler:
                handler(data_point, market=market)
            else:
                self._unknown_event_type_handler(data_point, market, stream_name,
                                            user_message="Can't find handler for event type")
        else:
            if "depth" in stream_name:
                event_type = "depthUpdate"
            elif "bookTicker" in stream_name:
                event_type = "bookTicker"
            else:
                self._unknown_event_type_handler(data_point, market, stream_name)
            
            handler = self.handler_tree[market]["e"].get(event_type)

            if handler:
                handler(data_point, market=market)
            else:
                self._unknown_event_type_handler(data_point, market, stream_name, 
                                            user_message="Can't find handler for event type")


    def _handle_multiple_data_points(self, data_points: list, market: str, stream_name: str):
        """
        Handle multiple data points.
        """
        for data_point in data_points:
            self._handle_single_data_point(data_point, market, stream_name)


    def _handle_error(self, error):
        """
        Handle an error.
        """
        error_code = error.get("code")
        error_message = error.get("msg")

        
        print(f"Error code {error_code}: {error_message}, {error}")
        time.sleep(1)
        #raise Exception(f"Error code {error_code}: {error_message}, {error}")


    def _handle_full_message(self, message, market: str):
        message = json.loads(message)
        if "data" in message and "stream" in message:
            data = message["data"]
            stream_name = message["stream"]

            if isinstance(data, list):
                # Multiple data points
                self._handle_multiple_data_points(data, market, stream_name)
            else:
                # Single data point
                self._handle_single_data_point(data, market, stream_name)
        
        else:
            # Error
            self._handle_error(message)
        
        if self.callback: 
            self.callback(message)


    def get_on_um_message_handler(self) -> callable:
        def on_um_message(_, message):
            self._handle_full_message(message, "um")
        return on_um_message

    
    def get_spot_message_handler(self) -> callable:
        def on_spot_message(_, message):
            self._handle_full_message(message, "spot")
        return on_spot_message



STREAM_DESCRIPTION = {
    "spot": {
        "aggTrade": {
            "name": "<symbol>@aggTrade",
            "parameters": {
                "symbol": "string",
            },
            "update_speed": "Real-time",
            "example": {
                "e": "aggTrade", # Event type
                "E": 123456789,  # Event time
                "s": "BNBBTC",   # Symbol
                "a": 12345,      # Aggregate trade ID
                "p": "0.001",    # Price
                "q": "100",      # Quantity
                "f": 100,        # First trade ID
                "l": 105,        # Last trade ID
                "T": 123456785,  # Trade time
                "m": True,       # Is the buyer the market maker?
                "M": True        # Ignore
            },
        },
        "trade": {
            "name": "<symbol>@trade",
            "parameters": {
                "symbol": "string",
            },
            "update_speed": "Real-time",
            "example": {
                "e": "trade",     # Event type
                "E": 123456789,   # Event time
                "s": "BNBBTC",    # Symbol
                "t": 12345,       # Trade ID
                "p": "0.001",     # Price
                "q": "100",       # Quantity
                "b": 88,          # Buyer order ID
                "a": 50,          # Seller order ID
                "T": 123456785,   # Trade time
                "m": True,        # Is the buyer the market maker?
                "M": True         # Ignore
            },
        },
        "kline": {
            "name": "<symbol>@kline_<interval>",
            "parameters": {
                "symbol": "string",
                "interval": {
                    "type": "enum",
                    "optional": False,
                    "enum": [
                        "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
                    ]
                },
            },
            "update_speed": "1000ms for 1s, 2000ms for others",
            "example": {
                "e": "kline",     # Event type
                "E": 123456789,   # Event time
                "s": "BNBBTC",    # Symbol
                "k": {
                    "t": 123400000, # Kline start time
                    "T": 123460000, # Kline close time
                    "s": "BNBBTC",  # Symbol
                    "i": "1m",      # Interval
                    "f": 100,       # First trade ID
                    "L": 200,       # Last trade ID
                    "o": "0.0010",  # Open price
                    "c": "0.0020",  # Close price
                    "h": "0.0025",  # High price
                    "l": "0.0015",  # Low price
                    "v": "1000",    # Base asset volume
                    "n": 100,       # Number of trades
                    "x": False,     # Is this kline closed?
                    "q": "1.0000",  # Quote asset volume
                    "V": "500",     # Taker buy base asset volume
                    "Q": "0.500",   # Taker buy quote asset volume
                    "B": "123456"   # Ignore
                }
            }
        },
        "miniTicker": {
            "name": "<symbol>@miniTicker",
            "parameters": {
                "symbol": "string",
            },
            "update_speed": "1000ms",
            "example": {
                "e": "24hrMiniTicker",  # Event type
                "E": 123456789,         # Event time
                "s": "BNBBTC",          # Symbol
                "c": "0.0025",          # Close price
                "o": "0.0010",          # Open price
                "h": "0.0025",          # High price
                "l": "0.0010",          # Low price
                "v": "10000",           # Total traded base asset volume
                "q": "18"               # Total traded quote asset volume
            }
        },
        "miniTickerAll": {
            "name": "!miniTicker@arr",
            "update_speed": "1000ms",
            "example": [
                # Same as miniTicker
            ],
        },
        "ticker": {
            "name": "<symbol>@ticker",
            "parameters": {
                "symbol": "string",
            },
            "example": {
                "e": "24hrTicker",  # Event type
                "E": 123456789,     # Event time
                "s": "BNBBTC",      # Symbol
                "p": "0.0015",      # Price change
                "P": "250.00",      # Price change percent
                "x": "0.0009",      # First trade(F)-1 price (first trade before the 24hr rolling window)
                "Q": "10",          # Last quantity
                "b": "0.0024",      # Best bid price
                "B": "10",          # Best bid quantity
                "a": "0.0026",      # Best ask price
                "A": "100",         # Best ask quantity
                "o": "0.0010",      # Open price
                "h": "0.0025",      # High price
                "l": "0.0010",      # Low price
                "c": "0.0025",      # Last price
                "w": "0.0020",      # Weighted average price
                "v": "10000",       # Total traded base asset volume
                "q": "18",          # Total traded quote asset volume
                "O": 0,             # Statistics open time
                "C": 86400000,      # Statistics close time
                "F": 0,             # First trade ID
                "L": 18150,         # Last trade Id
                "n": 18151          # Total number of trades
            },
        },
        "tickerAll": {
            "name": "!ticker@arr",
            "update_speed": "1000ms",
            "example": [
                # Same as ticker
            ],
        },
        "tickerWindow": {
            "name": "<symbol>@ticker_<window_size>",
            "parameters": {
                "symbol": "string",
                "window_size": {
                    "type": "enum",
                    "optional": False,
                    "enum": [
                        "1h", "4h", "1d",
                    ]
                },
            },
            "example": {
                "e": "24hrTicker",  # Event type
                "E": 123456789,     # Event time
                "s": "BNBBTC",      # Symbol
                "p": "0.0015",      # Price change
                "P": "250.00",      # Price change percent
                "o": "0.0010",      # Open price
                "h": "0.0025",      # High price
                "l": "0.0010",      # Low price
                "c": "0.0025",      # Last price
                "w": "0.0020",      # Weighted average price
                "v": "10000",       # Total traded base asset volume
                "q": "18",          # Total traded quote asset volume
                "O": 0,             # Statistics open time
                "C": 86400000,      # Statistics close time
                "F": 0,             # First trade ID
                "L": 18150,         # Last trade Id
                "n": 18151          # Total number of trades
            },
        },
        "tickerWindowAll": {
            "name": "!ticker_<window_size>@arr",
            "parameters": {
                "window_size": {
                    # Same as tickerWindow
                },
            },
            "update_speed": "1000ms",
            "example": [
                # Same as tickerWindow
            ],
        }, 
        "bookTicker": {
            "name": "<symbol>@bookTicker",
            "parameters": {
                "symbol": "string",
            },
            "update_speed": "Real-time",
            "example": {
                # No "e" field
                "u":400900217,      #  order book updateId
                "s":"BNBUSDT",      #  symbol
                "b":"25.35190000",  #  best bid price
                "B":"31.21000000",  #  best bid qty
                "a":"25.36520000",  #  best ask price
                "A":"40.66000000"   #  best ask qty
            }
        },
        "depth": {
            "name": "<symbol>@depth<levels>",
            "parameters": {
                "symbol": "string",
                "levels": {
                    "type": "enum",
                    "optional": False,
                    "enum": [
                        5, 10, 20,
                    ]
                },
                "update_speed": {
                    "type": "tag",
                    "optional": True,
                    "tag": ["@100ms"]
                }
            },
            "update_speed": "1000ms or 100ms",
            "example": {
                "lastUpdateId": 160,  # Last update ID
                "bids": [              # Bids to be updated
                    [
                        "0.0024",   # Price level to be updated
                        "10"        # Quantity
                    ]
                ],
                "asks": [              # Asks to be updated
                    [
                        "0.0026",   # Price level to be updated
                        "100"       # Quantity
                    ]
                ]
            }
        },
    },
    "um": {
        "e": {
            "aggTrade": {
                # Same as spot
            },
            "markPriceUpdate": {
                "name": "<symbol>@markPrice",
                "event_type": "markPriceUpdate",
                "parameters": {
                    "symbol": "string",
                    "update_speed": {
                        "type": "tag",
                        "optional": True,
                        "tag": ["@1s"]
                    }
                },
                "update_speed": "3s or 1s",
                "example": {
                    "e": "markPriceUpdate",  # Event type
                    "E": 1562305380000,     # Event time
                    "s": "BTCUSDT",         # Symbol
                    "p": "11185.87786641",  # Mark price
                    "i": "11154.40810491",  # Index price
                    "P": "11146.46706053",  # Estimated Settle Price, only useful in the last hour before the settlement starts
                    "r": "0.00030000",      # Funding rate
                    "T": 1562306400000      # Next funding time
                }
            },
            "markPriceUpdateAll": {
                "name": "!markPrice@arr",
                "event_type": "markPriceUpdate",
                "update_speed": "3s or 1s",
                "parameters": {
                    "update_speed": {
                        # Same as markPriceUpdate
                    }
                },
                "example": [
                    # Same as markPriceUpdate
                ],
            },
            "kline": {
                # Same as spot
            },
            "continuous_kline": {
                "name": "<pair>@continuousKline<contractType>_<interval>",
                "event_type": "continuous_kline",
                "update_speed": "250ms",
                "parameters": {
                    "pair": "string",
                    "contractType": {
                        "type": "enum",
                        "optional": False,
                        "enum": [
                            "PERPETUAL", "CURRENT_QUARTER", "NEXT_QUARTER",
                        ]
                    },
                    "interval": {
                        "type": "enum",
                        "optional": False,
                        "enum": [
                            "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
                        ]
                    },
                },
            },
            "miniTicker": {
                "update_speed": "500ms",
                # Same as spot
            },
            "miniTickerAll": {
                "update_speed": "1000ms",
                # Same as spot
            },
            "ticker": {
                "update_speed": "2000ms",
                # Same as spot
            },
            "tickerAll": {
                "update_speed": "1000ms",
                # Same as spot
            },
            "bookTicker": {
                # Same as spot
                "event_type": "bookTicker",
                "example": {
                    "e": "bookTicker",  # Event type
                    "u": 400900217,      # order book updateId
                    "E": 1568014460893,  # Event time
                    "T": 1568014460891,  # transaction time
                    "s": "BNBUSDT",      # symbol
                    "b": "25.35190000",  # best bid price
                    "B": "31.21000000",  # best bid qty
                    "a": "25.36520000",  # best ask price
                    "A": "40.66000000"   # best ask qty
                }
            },
            "bookTickerAll": {
                "name": "!bookTicker",
                "event_type": "bookTicker",
                "update_speed": "Real-time",
                "example": [
                    # Same as bookTicker
                ],
            },
            "forceOrder": {
                "name": "<symbol>@forceOrder",
                "event_type": "forceOrder",
                "update_speed": "1000ms",
                "parameters": {
                    "symbol": "string",
                },
                "example": {
                    "e": "forceOrder",  # Event type
                    "E": 1562305380000, # Event time
                    "o": {
                        "s": "BTCUSDT",         # Symbol
                        "S": "SELL",            # Side
                        "o": "LIMIT",           # Order type
                        "f": "IOC",             # Time in force
                        "q": "0.001",           # Original quantity
                        "p": "3000",            # Original price
                        "ap": "3000",           # Average price
                        "X": "FILLED",          # Order status
                        "l": "0.001",           # Order last filled quantity
                        "z": "0.001",           # Order filled accumulated quantity
                        "T": 1562305380000,     # Order trade time
                    }
                }
            },
            "forceOrderAll": {
                "name": "!forceOrder@arr",
                "event_type": "forceOrder",
                "update_speed": "1000ms",
                "example": {
                    # Same as forceOrder
                }
            },
            "depth": {
                "name": "<symbol>@depth<levels>",
                "event_type": "depthUpdate",
                "update_speed": "250ms, 500ms, 100ms (default 250ms)",
                "parameters": {
                    "levels": {
                        "type": "enum",
                        "optional": False,
                        "enum": [
                            5, 10, 20,
                        ]
                    },
                    "update_speed": {
                        "type": "tag",
                        "optional": True,
                        "tag": ["@100ms", "@500ms"]
                    }
                },
                "example": {
                    "e": "depthUpdate",  # Event type
                    "E": 1562305380000,  # Event time
                    "T": 1562305380000,  # transaction time
                    "s": "BTCUSDT",      # Symbol
                    "U": 157,            # first update ID in event
                    "u": 160,            # final update ID in event
                    "pu": 149,           # final update Id in last stream(ie `u` in last stream)
                    "b": [               # Bids to be updated
                        [
                            "0.0024",  # Price level to be updated
                            "10"       # Quantity
                        ]
                    ],
                    "a": [               # Asks to be updated
                        [
                            "0.0026",  # Price level to be updated
                            "100"      # Quantity
                        ]
                    ]
                }
            },
            "diff": {
                # Same as depth
                "example": {}
            },
            "compositeIndex": {
                "name": "<symbol>@compositeIndex",
                "event_type": "compositeIndex",
                "update_speed": "1000ms",
                "parameters": {
                    "symbol": "string",
                },
                "example": {}
            },
            "contractInfo": {},
            "assetIndex": {
                "name": "<assetSymbol>@assetIndex",
                "event_type": "assetIndexUpdate",
                "update_speed": "1s",
                "parameters": {
                    "assetSymbol": "string",
                },
                "example": {},
            },
            "assetIndexAll": {
                "name": "!assetIndex@arr",
                "event_type": "assetIndexUpdate",
                "update_speed": "1s",
                "example": [
                    # Same as assetIndex
                ],
            },
        },
        "user": {
            # <listenKey>@account, <listenKey>@balance, ...
            "MARGIN_CALL": {},
            "ACCOUNT_UPDATE": {},
            "ORDER_TRADE_UPDATE": {},
            "ACCOUNT_CONFIG_UPDATE": {},
            "STRATEGY_UPDATE": {},
            "GRID_UPDATE": {},
            "CONDITIONAL_ORDER_TRIGGER_REJECT": {},
        }
    },
}
