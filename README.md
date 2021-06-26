# Keylogger

#### Note:
   - **Created for educational purpose only!**
   - **You can use it on your own responsibility!**

This keylogger works on **Windows, Mac and Linux** operating systems indifferent from architecture.
The project contains the hacker side and the target side applications.

##### Hacker Side
The network communication is based on **TCP** connection, more specialy is created with ZeroMQ protocol. The hacker side creates two different type of ZeroMQ communication:
   1. publisher - subscriber
   2. request - reply

   The first one sends and receives the characters pressed by the target.
   The second one handles the menu options and the data received from this.
If the connection was **killed** (closed) by someone then the hacker side progresses emails which were sent by the **Target Side**.
While the network connection is stable it has 4 options:
   1. Take screenshot
   2. Webcam picture
   3. Record audio
   4. Exit

   The first option takes a screenshot from the target's pc and sends it through the network.
   The second option takes a webcam picture with the target's pc and sends it through the network.
   The third option records a 10 seconds audio with the target's pc and sends it through the network.
   The fourth option exits from the ZeroMQ connection.

##### Target Side
The target has two different communication types as well as the hacker side. The pub - sub is a one way communication which means the target sends data and the hacker receives it. The request - reply is a two way communication which means both sides can send and receive data.
If the connection was **killed** (closed) the target side saves the keyboard data into a file under Windows' local Temp directory and sends email with attachments to the *hacker*. (__attachments__: *keyboard data*, *screenshot*)

## Usage
   ##### Hacker
   In *config.ini* under *GMAIL_SERVICE* has to be changed:
   - `EmailAddress = "gmail address"`
   - `EmailPassword = "gmail password"`
   - __optional__: `portStream`
   - __optional__: `portInteract`

   In *TargetApp.pyw* has to be changed:
   - `ip_address = "your own ip"`
   - `email_address = "gmail address"`
   - `email_password = "gmail password"`
   - __optional__: `port_stream`
   - __optional__: `port_interact`

   - the hacker has to open three ports
      1. stream port for ZeroMQ
      2. interact port for ZeroMQ
      3. a port for a server to download the keylogger
   - run `python3 HackerApp.py` and wait for the connection
   - makes the USB Rubber Ducky