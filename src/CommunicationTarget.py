import zmq, pickle
import time
from base64 import b64encode
from urllib.request import urlopen, Request
from ICommunication import ICommunication


class CommunicationTarget(ICommunication):
	def __init__(self, ip_address, port_stream, port_interact):
		super(CommunicationTarget, self).__init__(ip_address=ip_address,
			port_stream=port_stream, port_interact=port_interact)


	def connect2stream(self):
		self.stream_context = zmq.Context()
		self.socket_stream = self.stream_context.socket(zmq.PUB)
		self.socket_stream.connect('tcp://' + self.ip_address + ':' + str(self.port_stream))

		try:
			self.pc_ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
		except Exception:
			self.pc_ip = "Unknown"

		time.sleep(0.1)
		msg = 'OK'.encode()
		msg = b64encode(msg)
		msg = pickle.dumps(msg)
		self.socket_stream.send(msg)


	def connect2interaction(self):
		self.interact_context = zmq.Context()
		self.socket_interact = self.interact_context.socket(zmq.REP)
		self.socket_interact.connect('tcp://' + self.ip_address + ':' + str(self.port_interact))