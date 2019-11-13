import socket
import random

class HostClient:

	socket_to_server = None
	server_port = 0

	#Constructor
	def __init__(self):
		self.listening_port = random.randint(20000,65500)
		self.connected = False
		self.socket_to_server = socket.socket()

	#Connect to Server
	def connect(self,addr,port):
		success = self.socket_to_server.connect_ex((addr,port))
		return (success == 0)

	#Send credentials and file list
	def sendCredentials(self,un,host,speed):

		#Send creds to server
		credentials = "{} {} {}".format(un,host,speed)
		self.socket_to_server.send(credentials.encode())

		#wait for 'OK' response
		ans = self.socket_to_server.recv(1024)
		if(ans != b"OK"):
			return("Error on credential handshake")

		#send list of files to server
		fp = open("files.json","rb")
		json_data = fp.read()
		self.socket_to_server.send(json_data)

		return("Connected")

	#query server for files with keyword in them
	def search(self,keyword):
		msg = "search {}".format(keyword)
		self.socket_to_server.send(msg.encode())

		#get answer
		files_data = self.socket_to_server.recv(1024)
		files_str = files_data.decode()

		return files_str

	def close(self):
		if(not self.connected):
			return
		self.socket_to_server.send(b"exit")
		self.socket_to_server.close()
		self.connected = False

	def getFile(self,fname):
		self.socket_to_server.send(fname.encode())
		fp = open(fname,"wb")
		while True:
			data = self.socket_to_server.recv(1024)
			if(data == b"DONE"):
				break
			fp.write(data)
		fp.close()
		return "File recieved"
