import socket
import random
import threading
import time

class HostServer(threading.Thread):

	def __init__(self):

		self.port = random.randint(20000,65000)
		listen_thread = threading.Thread(target=self.listen)
		listen_thread.daemon = True
		listen_thread.start()

	def getHostInfo(self):
		hn = socket.gethostname()
		ipadd = socket.gethostbyname(hn)
		ans = "{}:{}:{}".format(hn,ipadd,self.port)
		ans = ans.replace(' ','')
		return ans

	def listen(self):

		serversock = socket.socket()
		serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		serversock.bind(('',self.port))
		serversock.listen(4)

		while True:

			clientsock, addr = serversock.accept()
			#print("Connection from {}".format(addr))
			cthread = threading.Thread(target=self.sendFile,args=(clientsock,addr))
			cthread.daemon = True
			cthread.start()

	def sendFile(self,csock,addr):

		file_name = csock.recv(1024).decode()

		fp = open(file_name,"rb")
		data = fp.read(1024)
		while data:
			csock.send(data)
			data = fp.read(1024)
		fp.close()
		time.sleep(0.5)
		csock.send(b"DONE")
		#print("File Sent")

		csock.close()