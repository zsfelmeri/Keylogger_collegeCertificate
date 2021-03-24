import zmq
import base64


class CommunicationHacker:
	def __init__(self, ip_address, port_stream, port_interact):
		self.ip_address = ip_address
		self.port_stream = port_stream
		self.port_interact = port_interact


	def connect2stream(self):
		self.stream_context = zmq.Context()
		self.socket_stream = self.stream_context.socket(zmq.SUB)
		self.socket_stream.bind('tcp://' + self.ip_address + ':' + str(self.port_stream))
		self.socket_stream.subscribe('')

		msg = self.socket_stream.recv_string()
		if base64.b64decode(msg).decode() != 'OK':
			raise Exception('Connection failed!')


	def connect2interaction(self):
		self.interact_context = zmq.Context()
		self.socket_interact = self.interact_context.socket(zmq.REQ)
		self.socket_interact.bind('tcp://' + self.ip_address + ':' + str(self.port_interact))