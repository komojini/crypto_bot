import os

from binance.spot import Spot
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

from .message_handler import BinanceWSMessageHandler
from crypto_bot.utils.util import get_yes_or_no_input


class BinanceClient:
	def __init__(
		self,
		api_key=None,
		secret_key=None,
		message_handler: BinanceWSMessageHandler = None,
	):
		
		self.message_handler = message_handler

		self.um_client: UMFutures = None
		self.spot_client: Spot = None

		self.spot_listen_key = None
		self.um_listen_key = None

		self._auth_and_get_listen_key(api_key, secret_key)

		self.spot_ws_stream_client: SpotWebsocketStreamClient = None
		self.um_ws_client: UMFuturesWebsocketClient = None

		self._initialize_websockets()

	def _auth_and_get_listen_key(self, api_key, secret_key) -> None:
		"""
		Authenticate the user by either using the api key and secret key passed in
		or by using the api key and secret key stored in the environment variables.
		"""
		if api_key is None or secret_key is None:
			api_key = os.environ.get("BINANCE_API_KEY")
			secret_key = os.environ.get("BINANCE_SECRET_KEY")

		if api_key is None or secret_key is None:
			if get_yes_or_no_input("No api key or secret key found.\n \
						  			Continue without authentication?\n \
									Creating order and streaming user data will not be available.\n \
						  			(y/n): "):
				self.spot_client = Spot()
				self.um_client = UMFutures()
				return
			else:
				self._auth_by_input()
				return
		
		elif not self._api_key_is_valid(api_key, secret_key):
			self._auth_by_input()
			return 
		
		self.spot_client = Spot(api_key, secret_key)
		self.um_client = UMFutures(api_key, secret_key)
		self._update_listen_keys()
		print("\n\nAuthentication successful.\n\n")

	def _auth_by_input(self):
		"""
		Authenticate the user by using the api key and secret key passed in.
		"""
		while True:
			api_key = input("Enter api key: ").strip()
			secret_key = input("Enter secret key: ").strip()
			
			if not self._api_key_is_valid(api_key, secret_key): 	
				if get_yes_or_no_input("Invalid api key or secret key.\n \
										Try again?\n \
										(y/n): "):
					continue
				else:
					print("\n\nContinuing without authentication.\n\n")
					self.spot_client = Spot()
					self.um_client = UMFutures()
					return
			
	def _api_key_is_valid(self, api_key, secret_key) -> bool:
		self.spot_client = Spot(api_key, secret_key)
		self.um_client = UMFutures(api_key, secret_key)
		try:
			self._update_listen_keys()
			return True
		except Exception as e:
			print("Error: ", e)
			return False
	
	def _update_listen_keys(self) -> None:
		self.spot_listen_key = self.spot_client.new_listen_key()["listenKey"]
		self.um_listen_key = self.um_client.new_listen_key()["listenKey"]
			
	def _initialize_websockets(self) -> None:
		self.spot_ws_stream_client = SpotWebsocketStreamClient(
			on_message=self.message_handler.get_spot_message_handler(),
			is_combined=True,
		)
		self.um_ws_client = UMFuturesWebsocketClient(
			on_message=self.message_handler.get_on_um_message_handler(),
			is_combined=True,
		)

	def start_user_data_streams(self) -> None:
		self.spot_ws_stream_client.user_data(
			listen_key=self.spot_listen_key,
			id=1,
		)
		self.um_ws_client.user_data(
			listen_key=self.um_listen_key,
			id=2,
		)

	def close_user_data_streams(self) -> None:
		self.spot_ws_stream_client.stop()
		self.um_ws_client.stop()
	
	def stream_pairs(self, 
					 pairs: list,
					 types: list,
					 spot: bool = True,
					 futures: bool = False) -> None:
		"""
		Stream the data for the specified pairs and types.
		Args:
			pairs (list): The pairs to stream.
			types (list): The types of data to stream. (e.g. ["aggTrade", "kline_1m"])
				Can be found here: https://binance-docs.github.io/apidocs/voptions/en/#live-subscribing-unsubscribing-to-streams
			
		"""
		if types == []:
			types = ["aggTrade"]
		
		stream = []
		for pair in pairs:
			for type in types:
				stream.append(f"{pair}@{type}")
		
		self.start_stream(
			spot_streams=stream if spot else None,
			um_streams=stream if futures else None,
		)

	def start_stream(self,
			   spot_streams: list = None,
			   um_streams: list = None) -> None:	
		
		if spot_streams:
			self.spot_ws_stream_client.subscribe(
				stream=spot_streams,
			)
		if um_streams:
			self.um_ws_client.subscribe(
				stream=um_streams,
			)

	def stop_stream(self) -> None:
		"""Stop both the spot and futures streams."""
		self.spot_ws_stream_client.stop()
		self.um_ws_client.stop()
