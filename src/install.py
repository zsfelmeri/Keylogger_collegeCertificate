import sys, os, platform, subprocess, threading

if len(sys.argv) != 2:
	print("Usage: python3.x <requirments file>")
	sys.exit(1)

system_name = platform.system().lower()
architecture = platform.architecture()
whl_installed = False

pyaudio_wheels32 = [
	"PyAudio‑0.2.11‑cp39‑cp39‑win32.whl",
	"PyAudio‑0.2.11‑cp38‑cp38‑win32.whl",
	"PyAudio‑0.2.11‑cp37‑cp37m‑win32.whl",
	"PyAudio‑0.2.11‑cp36‑cp36m‑win32.whl",
	"PyAudio‑0.2.11‑cp35‑cp35m‑win32.whl",
	"PyAudio‑0.2.11‑cp34‑cp34m‑win32.whl",
	"PyAudio‑0.2.11‑cp27‑cp27m‑win32.whl"
]

pyaudio_wheels64 = [
	"PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl",
	"PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl",
	"PyAudio‑0.2.11‑cp37‑cp37m‑win_amd64.whl",
	"PyAudio‑0.2.11‑cp36‑cp36m‑win_amd64.whl",
	"PyAudio‑0.2.11‑cp35‑cp35m‑win_amd64.whl",
	"PyAudio‑0.2.11‑cp34‑cp34m‑win_amd64.whl",
	"PyAudio‑0.2.11‑cp27‑cp27m‑win_amd64.whl"
]

try:
	subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", sys.argv[1]])
except subprocess.CalledProcessError as err:
	print(err)

if system_name == 'windows':
	def download_wheel(whl):
		subprocess.check_call(["curl", f"https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio/{whl}", "-o", whl])


	def install_wheel(whl):
		subprocess.check_call([sys.executable, "-m", "pip", "install", whl])


	if architecture == '32bit':
		for whl in pyaudio_wheels32:
			try:
				download_thread = threading.Thread(target=download_wheel, args=(whl,))
				download_thread.start()
				download_thread.join()

				install_thread = threading.Thread(target=install_wheel, args=(whl,))
				install_thread.start()
				install_thread.join()

				os.remove(whl)
			except subprocess.CalledProcessError as err:
				print(err)
	elif architecture == '64bit':
		for whl in pyaudio_wheels64:
			try:
				download_thread = threading.Thread(target=download_wheel, args=(whl,))
				download_thread.start()
				download_thread.join()

				install_thread = threading.Thread(target=install_wheel, args=(whl,))
				install_thread.start()
				install_thread.join()

				os.remove(whl)
			except subprocess.CalledProcessError as err:
				print(err)
elif system_name == 'darwin':
	def download_brew():
		subprocess.check_call(["/bin/bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])

	try:
		download_thread = threading.Thread(target=download_brew)
		download_thread.start()
		download_thread.join()

		subprocess.check_call(["xcode-select", "--install"])
		subprocess.check_call(["brew", "install", "portaudio"])
		subprocess.check_call([sys.executable, "-m", "pip", "install", "pyaudio"])
	except subprocess.CalledProcessError as err:
		print(err)