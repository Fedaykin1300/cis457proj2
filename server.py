import socket
import json
import threading

#listening port
PORT = 13377

#dictionary of connected clients
clients = {}

#Holds Client info and search method
class Client:

	def __init__(self,username,address,speed,files_dict):
		self.username = username
		self.address = address
		self.speed = speed
		self.files_dict = files_dict

	#returns dictionary
	def searchFiles(self,keyword):
		filenames = []
		for file in self.files_dict['files']:
			fname = file['filename']
			descs = file['descriptions']
			matching = [d for d in descs if keyword in d]
			if(matching):
				filenames.append(fname)
		if(not filenames):
			return {}
		else:
			return {'username':self.username,'address':self.address,'speed':self.speed,'files':filenames}


#Called for each new client connection
def new_client(clientsocket,addr):

	#credentials = username/host/speed
	credentials = clientsocket.recv(1024).decode().split()
	username = credentials[0]
	host = credentials[1]
	speed = credentials[2]
	print(f"un:{username}  host:{host}  speed:{speed}")

	#send acknowledgement
	clientsocket.send(b"OK")

	#get files from host
	files_data = clientsocket.recv(3048)
	files_dict = json.loads(files_data)
	num_files = len(files_dict['files'])
	print("{} connected with {} files".format(username,num_files))

	#add to client dictionary
	print("Adding client to dictionary")
	clients[username] = Client(username,
								host,
								speed,
								files_dict)

	#Loop to read and process client input
	while True:

		msg = clientsocket.recv(1024).decode()

		if(not msg):
			print("No message, client probably quit.")
			del clients[username]
			clientsocket.close()
			break

		words = msg.split()

		#Client is searching for files
		if(words[0] == "search"):
			print(f"{username}: Searching for: {words[1]}")
			accumulation = []							#list of dictionaries
			for k in clients:							#for each client in client dictionary
				d = clients[k].searchFiles(words[1])	#dictionary from client
				if(not d):								#No matching files in client
					continue
				accumulation.append(d)					#add to list

			if(not accumulation):						#No matching files from anyone
				clientsocket.send(b"none")
			else:
				data = json.dumps(accumulation)			#store info in json
				clientsocket.send(data.encode())		#send json info to client

		#Client is disconnecting
		if(words[0] == "quit" or words[0] == "exit"):
			print(f"{username}: Quiting")
			clientsocket.close()
			del clients[username]
			break


def main():
	print("Server listening on port {}".format(PORT))

	sock = socket.socket()
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('',PORT))
	sock.listen(4)

	while True:
		clientsock,addr = sock.accept()
		print("Connection from {}".format(addr))
		client_thread = threading.Thread(target=new_client,args=(clientsock,addr))
		client_thread.start()

	sock.close()

if __name__ == "__main__":
	main()