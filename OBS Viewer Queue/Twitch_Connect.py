import socket
import time
import obspython as obs

class TwitchIRC:
	def __init__(self, chan="", nick="", passw="", host="irc.twitch.tv", port=6667):
		self.channel = chan
		self.nickname = nick
		self.password = passw
		self.host = host
		self.port = port

		self.rate_num_msgs = 19  # Number of messages allowed...
		self.rate_timeframe = 30  # ...in timeframe of x seconds
		self.__message_timestamps = []

		self.__connected = False
		self.__last_message = None  # Last connection timestamp
		self.timeout = 10.0  # Time before open connection is closed, in seconds

		self.__sock = socket.socket()

	def connect(self, suppress_warnings=True):
		connection_result = self.__connect()

		if connection_result is not True:
			self.__connected = False
			if suppress_warnings:
				print("Connection Error:", connection_result)
				return False
			else:
				raise UserWarning(connection_result)

		self.__connected = True
		return True

	def __connect(self):
		if self.__connected:
			return True  # Already connected, nothing to see here

		self.__sock = socket.socket()
		self.__sock.settimeout(1)  # One second to connect

		try:
			self.__sock.connect((self.host, self.port))
		except socket.gaierror:
			return "Cannot find server"
		except (TimeoutError, socket.timeout):
			return "No response from server (connection timed out)"

		if self.password is not "":
			self.__sock.send("PASS {}\r\n".format(self.password).encode("utf-8"))
		self.__sock.send("NICK {}\r\n".format(self.nickname).encode("utf-8"))
		self.__sock.send("JOIN #{}\r\n".format(self.channel).encode("utf-8"))

		auth_response = self.read()
		if "Welcome, GLHF!" not in auth_response:
			return "Bad Authentication! Check your Oauth key"

		try:
			self.read()  # Wait for "JOIN" response
		except socket.timeout:
			return "Channel not found!"

		return True

	def disconnect(self):
		if self.__connected:
			self.__sock.shutdown(socket.SHUT_RDWR)
			self.__sock.close()
			self.__connected = False

	def connection_timeout(self):
		if self.__connected and time.time() >= self.__last_message + self.timeout:
			self.disconnect()

	def test_authentication(self):
		if self.connect(False):
			self.disconnect()
		print("Authentication successful!")

	def chat(self, msg, suppress_warnings=True):
		if not self.check_rates() or not self.connect(suppress_warnings):
			return

		# Store timestamps for rate limit and connection timeout
		message_time = time.time()
		self.__message_timestamps.append(message_time + self.rate_timeframe)
		self.__last_message = message_time

		self.__chat_direct(msg)
		print("Sent \'" + msg + "\'", "as", self.nickname, "in #" + self.channel)

	def __chat_direct(self, msg):
		self.__sock.send("PRIVMSG #{} :{}\r\n".format(self.channel, msg).encode("utf-8"))

	def read(self):
		response = self.__read_socket()
		while self.__ping(response):
			response = self.__read_socket()
		return response.rstrip()

	def __read_socket(self):
		return self.__sock.recv(1024).decode("utf-8")

	def __ping(self, msg):
		if msg[:4] == "PING":
			self.__pong(msg[4:])
			return True
		return False

	def __pong(self, host):
		self.__sock.send(("PONG" + host).encode("utf-8"))

	def check_rates(self):
		index = 0

		# Remove timestamps that have passed
		for index, timestamp in enumerate(self.__message_timestamps):
			if time.time() <= timestamp:
				break
		self.__message_timestamps = self.__message_timestamps[index:]

		# If at max rate, throw an error
		if len(self.__message_timestamps) >= self.rate_num_msgs:
			next_clear = int(self.__message_timestamps[0] - time.time())
			msg_plural = "s"

			if next_clear <= 1:
				next_clear = 1  # Avoiding "wait 0 more seconds" messages
				msg_plural = ""

			print("Error: Rate limit reached. Please wait " + str(next_clear) + " more second" + msg_plural)
			return False

		return True

twitch = TwitchIRC()


def check_connection():
	twitch.connection_timeout()

def test_authentication(prop, props):
	twitch.test_authentication()