import tkinter as tk
from hostclient import HostClient
from hostserver import HostServer
import json

class HostGUI:

	root = None
	file_dict = {}
	connected = False

	def __init__(self,hclient,hserver):
		self.host_client = hclient
		self.host_server = hserver

	def isconnected(func):
		def wrapper(self):
			if self.connected:
				func(self)
			else:
				self.log("...Not Connected Yet!","coral1")
		return wrapper

	def setupGUI(self):
		self.root = tk.Tk()
		self.root.title("FTP Host")
		self.root.config(padx=10,pady=10)

		#connection frame
		connection_group = tk.LabelFrame(self.root,
										text="Connection",
										padx=5,
										pady=5)
		connection_group.grid(row=0,column=0)
		server_label = tk.Label(connection_group,text="Sever Hostname:")
		server_label.grid(row=0,column=0)
		self.server_entry = tk.Entry(connection_group)
		self.server_entry.grid(row=0,column=1)
		port_label = tk.Label(connection_group,text="Port:")
		port_label.grid(row=0,column=2)
		self.port_entry = tk.Entry(connection_group)
		self.port_entry.grid(row=0,column=3)
		connect_button = tk.Button(connection_group,text="Connect",width=15,command=self.connectToServer)
		connect_button.grid(row=0,column=4,columnspan=2,padx=10)
		username_label = tk.Label(connection_group,text="Username:")
		username_label.grid(row=1,column=0)
		self.username_entry = tk.Entry(connection_group)
		self.username_entry.grid(row=1,column=1)
		hostname_label = tk.Label(connection_group,text="Hostname:")
		hostname_label.grid(row=1,column=2)
		self.hostname_text = tk.StringVar()
		self.hostname_entry = tk.Entry(connection_group,textvariable=self.hostname_text)
		self.hostname_text.set(self.host_server.getHostInfo())
		self.hostname_entry.grid(row=1,column=3)
		speed_label = tk.Label(connection_group,text="Speed:")
		speed_label.grid(row=1,column=4,padx=10)
		self.speed_val = tk.StringVar(self.root)
		self.speed_val.set("Ethernet")
		self.speed_menu = tk.OptionMenu(connection_group,
									self.speed_val,
									"Ethernet",
									"T1",
									"28.8k",
									"56k",
									"Cup and String",
									"DSL")
		self.speed_menu.grid(row=1,column=5)


		#Search Frame
		search_group = tk.LabelFrame(self.root,text="Search",padx=5,pady=5)
		search_group.grid(row=1,column=0,sticky="W")
		keyword_label = tk.Label(search_group,text="Keyword:")
		keyword_label.grid(row=0,column=0,sticky="W")
		self.keyword_entry = tk.Entry(search_group,width=29)
		self.keyword_entry.grid(row=0,column=1,sticky="W")
		search_button = tk.Button(search_group,text="Search",command=self.searchForFile)
		search_button.grid(row=0,column=2)
		retrieve_button = tk.Button(search_group,text="Retrieve",command=self.retrieveButton)
		retrieve_button.grid(row=0,column=3)
		self.search_listbox = tk.Listbox(search_group,width=70,height=8,selectmode='multiple')
		self.search_listbox.grid(row=1,column=0,columnspan=4,sticky="NS")
		#Vertical scrollbar
		search_scroll_v = tk.Scrollbar(search_group,orient=tk.VERTICAL)
		search_scroll_v.grid(row=1,column=0,columnspan=4,sticky="NSE")
		search_scroll_v.config(command=self.search_listbox.yview)
		self.search_listbox.config(yscrollcommand=search_scroll_v.set,font=("courier new",10,"normal"))
		#horizontal scrollbar
		search_scroll_h = tk.Scrollbar(search_group,orient=tk.HORIZONTAL)
		search_scroll_h.grid(row=1,column=0,columnspan=4,sticky="ESW")
		search_scroll_h.config(command=self.search_listbox.xview)
		self.search_listbox.config(xscrollcommand=search_scroll_h)

		#ftp group
		ftp_group = tk.LabelFrame(self.root,text="FTP",padx=5,pady=5)
		ftp_group.grid(row=2,column=0,sticky="W")
		command_label = tk.Label(ftp_group,text="Enter Command:")
		command_label.grid(row=0,column=0)
		self.command_entry = tk.Entry(ftp_group,width=40)
		self.command_entry.grid(row=0,column=1)
		go_button = tk.Button(ftp_group,text="Go",width=10,command=self.ftpButton)
		go_button.grid(row=0,column=2,padx=10)


		self.log_listbox = tk.Listbox(ftp_group,width=80)
		self.log_listbox.grid(row=1,column=0,columnspan=3,sticky="NS")
		log_scroll = tk.Scrollbar(ftp_group,orient=tk.VERTICAL)
		log_scroll.grid(row=1,column=0,columnspan=3,sticky="NSE")
		log_scroll.config(command=self.log_listbox.yview)
		self.log_listbox.config(yscrollcommand=log_scroll.set)



		self.root.protocol("WM_DELETE_WINDOW",self.close)
		self.root.mainloop()


	#Connect to server
	def connectToServer(self):
		#Parsing Server INfo
		addr = self.server_entry.get()
		port = int(self.port_entry.get())
		conn_str = "Connecting to {} : {}".format(addr,port)
		self.log(conn_str,"white")

		#attempting connection
		success = self.host_client.connect(addr,port)
		if(success):
			self.log("...Successfully Connected to Server","pale green")
			self.connected = True
		else:
			self.log("...Error Connecting to Server","coral1")
			return

		#Parsing credentials
		un = self.username_entry.get()
		host_str = self.hostname_entry.get()
		speed = self.speed_val.get()
		cred_str = "Username: {}    Host: {}    Speed: {}".format(un,host_str,speed)
		self.log(cred_str,"white")
		#send credentials
		self.host_client.sendCredentials(un,host_str,speed)

	#Search server for files
	@isconnected
	def searchForFile(self):

		kw = self.keyword_entry.get()

		if(not kw):
			self.log("...No string","coral1")
			return

		srch_str = "Searching for {}".format(kw)
		self.log(srch_str,"white")

		#send search keyword to server and get response
		ans = self.host_client.search(kw)
		
		#parse json data sent by server of list of files
		self.search_listbox.delete(0,tk.END)
		self.file_dict.clear()

		#No files found
		if(ans == "none"):
			self.search_listbox.insert(tk.END, "No files")
			self.log("...No Files Found","coral1")
			return

		#parse file json info
		header_str = "{:<30}{:<15}{:<25}".format("Filename","Username","Host")
		self.search_listbox.insert(tk.END, header_str)
		clients = json.loads(ans)
		for c in clients:
			for f in c['files']:
				data_str = "{:<30.28}{:<15.13}{}   ".format(f,c['username'],c['address'])
				self.search_listbox.insert(tk.END, data_str)
				self.file_dict[f] = (c['address'])
		self.log("...{} Files Found".format(len(self.file_dict)),"pale green")

	#Button in search group, download selected items
	@isconnected
	def retrieveButton(self):

		#tuple of selected lines
		line_nums = self.search_listbox.curselection()

		#Bad selections
		if(line_nums == () or 0 in line_nums):
			self.log("...Bad Selection","coral1")
			return

		#handle all selected lines and retrieve those files
		for l in line_nums:
			line = self.search_listbox.get(l)
			fname = line.split()[0]
			self.retrieveFile(fname)


	#Handles button in ftp group
	@isconnected
	def ftpButton(self):
		filename = self.command_entry.get()
		self.retrieveFile(filename)

	#Get info from server
	def retrieveFile(self,filename):
		
		cmnd_str = "Retrieving file {}".format(filename)
		self.log(cmnd_str,"white")

		#get host info
		file_host = self.file_dict.get(filename,"")
		if(not file_host):
			self.log("...No file found","coral1")
			return

		#Connect to host
		host_parts = file_host.split(':')
		host_addr = host_parts[1]
		host_port = int(host_parts[2])
		self.log("{} : {}".format(host_addr,host_port),"white")
		temp_client = HostClient()
		success = temp_client.connect(host_addr,host_port)

		if(not success):
			self.log("...Error Connecting to Host","coral1")
			return
		else:
			self.log("...Successfully Connected To Client","pale green")

		temp_client.getFile(filename)

		self.log("File Recieved","pale green")

	def log(self,msg,color):
		self.log_listbox.insert(tk.END,msg)
		self.log_listbox.yview(tk.END)
		self.log_listbox.itemconfig(tk.END, bg=color)

	def close(self):
		self.host_client.close()
		self.root.destroy()


def main():
	host_client = HostClient()
	host_server = HostServer()

	gui = HostGUI(host_client,host_server)
	gui.setupGUI()

if __name__ == "__main__":
	main()