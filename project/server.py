#################################
# Author: Scott McCoy           #
# Course: CSCI 156              #
# Term Project Fall 2017        #
#################################

import socketserver
import socket
import time
import os
import random
import glob

def now():
	return time.ctime(time.time())

#-------------------------------------------------
# GLOBAL DECLARATIONS

#keep track of the number of clients connected
num_clients = 2
connected_clients = 0
clients_done = 0

#lists of prices for the stocks
AAPL = [] #apple
GOOG = [] #google
INTC = [] #intel
RHT  = [] #redhat
IBM  = [] #IBM
FB   = [] #facebook
#-------------------------------------------------

#main class for running the server
class TCPClientHandler(socketserver.BaseRequestHandler):
	
	def getNewPrices(self):	
		global AAPL #apple
		global GOOG #google
		global INTC #intel
		global RHT  #redhat
		global IBM  #IBM
		global FB   #facebook

		print('#> Server advancing prices')
		if len(AAPL) <= 1:
			print('#> Final price has been read, exiting')
			quit()
		#get rid of old price for every stock
		del AAPL[0] 
		del GOOG[0] 
		del INTC[0] 
		del RHT[0]
		del IBM[0]
		del FB[0]

	def getPrice(self, stock):
		global AAPL #apple
		global GOOG #google
		global INTC #intel
		global RHT  #redhat
		global IBM  #IBM
		global FB   #facebook

		if stock == 'AAPL':
			return AAPL[0]
		elif stock == 'GOOG':
			return GOOG[0]
		elif stock == 'INTC':
			return INTC[0]
		elif stock == 'RHT':
			return RHT[0]
		elif stock == 'IBM':
			return IBM[0]
		else:
			return FB[0]

	def waitForClients(self):
		#this function waits until the specified number of clients
		#connects before proceding to perform operations
		global num_clients
		global connected_clients

		print('Connection opened with', self.client_address, 'at', now())
		connected_clients = connected_clients + 1

		while connected_clients < num_clients:
			print('There are currently', connected_clients, 'clients connected. Waiting for more')
			time.sleep(1)
			
		reply = 'Check-in recieved by the server'
		self.request.send(reply.encode())
		time.sleep(1)

	def getRequestStatus(self):
		if random.randint(1,10) == 1:
			status = 'FAILED'
		else:
			status = 'SUCCESS'

		return status

	def handle(self):
		global clients_done
		self.waitForClients()

		#This block of code processes regular requests
		while True:
			#----------------------------------------------------------------
			#Server recieves 'Name, Action, Stock'(incoming message size 35 bytes)
			data = self.request.recv(35)
			if not data:
				break
			print('#> Server recieved %s at %s' % (data, now()))
			#data is in the form 'Name, Action, Stock'
			data = data.decode('utf-8')
			data = data.rstrip('0')
			data = data.split(',')
			#----------------------------------------------------------------


			#----------------------------------------------------------------
			#server sends back 'status, stock, price' (recv buffer 35 bytes)
			status = self.getRequestStatus()
			reply = status + ',' + data[2] + ',' + str(self.getPrice(data[2]))
			reply = reply.encode() #convert message to bytes
			reply += b'0' * (35 - len(reply)) #appends 0 to message until it meets the required length
			self.request.send(reply)
			#----------------------------------------------------------------


			#----------------------------------------------------------------
			#Server recieves 'client_x Ready' when the client is done for this round
			data = self.request.recv(14) #this will be 14 bytes for x = 0-9
			if not data:
				break

			print('#> Server recieved %s at %s' % (data, now()))
			data = data.decode('utf-8')
			data = data.split(' ')
			#----------------------------------------------------------------


			#------------------------------------------------------------------------ 
			#this block makes the clients wait for any remaining clients
			#to finish their transactions before the server is allowed to
			#proceed and supply a new set of prices
			if data[1] == 'Ready':
				clients_done = clients_done + 1
				while clients_done < num_clients:
					print('#>', data[0], 'waiting for other clients to finish')
					time.sleep(0.5) #this sleep is to help reduce terminal spam
				#makes sure that the other client has time to check the conditional
				#for the while loop so we don't deadlock
				time.sleep(1) 	
				if data[0] == 'client_1':
					self.getNewPrices
					clients_done = 0

			else:
				print('#> ERROR!')
			#------------------------------------------------------------------------


			#----------------------------------------------------------------
			reply = 'Proceed'
			self.request.send(reply.encode())
			#----------------------------------------------------------------

		self.request.close()

#class for keeping track of all the data
class Stockserver():

	def startHandler(self, addr):
		#handle requests until we recieve a shutdown request
		server = socketserver.ThreadingTCPServer(myaddr, TCPClientHandler)
		server.serve_forever()

	def initilizePrices(self):
		global AAPL #apple
		global GOOG #google
		global INTC #intel
		global RHT  #redhat
		global IBM  #IBM
		global FB   #facebook

		print('#> Initilizing price data')
		files = glob.glob('prices/*.csv')

		for file in files:
			print('Reading', file)
			stock_name = file.replace('prices/','')
			stock_name = stock_name.replace('.csv', '')	
			
			if stock_name == 'AAPL':
				with open(file, 'r') as f:
					for line in f:
						price = line.split(',')
						if price[0] == 'Date':
							continue
						price = round(float(price[3]), 2) 
						#now we have a nice rounded decimal for price so store it in the list
						AAPL.append(price)
			elif stock_name == 'GOOG':
				with open(file, 'r') as f:
					for line in f:
						price = line.split(',')
						if price[0] == 'Date':
							continue
						price = round(float(price[3]), 2) 
						#now we have a nice rounded decimal for price so store it in the list
						GOOG.append(price)
			elif stock_name == 'INTC':
				with open(file, 'r') as f:
					for line in f:
						price = line.split(',')
						if price[0] == 'Date':
							continue
						price = round(float(price[3]), 2) 
						#now we have a nice rounded decimal for price so store it in the list
						INTC.append(price)
			elif stock_name == 'RHT':
				with open(file, 'r') as f:
					for line in f:
						price = line.split(',')
						if price[0] == 'Date':
							continue
						price = round(float(price[3]), 2) 
						#now we have a nice rounded decimal for price so store it in the list
						RHT.append(price)
			elif stock_name == 'IBM':
				with open(file, 'r') as f:
					for line in f:
						price = line.split(',')
						if price[0] == 'Date':
							continue
						price = round(float(price[3]), 2) 
						#now we have a nice rounded decimal for price so store it in the list
						IBM.append(price)
			elif stock_name == 'FB':
				with open(file, 'r') as f:
					for line in f:
						price = line.split(',')
						if price[0] == 'Date':
							continue
						price = round(float(price[3]), 2) 
						#now we have a nice rounded decimal for price so store it in the list
						FB.append(price)
			else:
				print('ERROR: Unrecognized stock in initilizePrices')

if __name__ == '__main__':
	server = Stockserver()
	server.initilizePrices() #reads prices in from price lists
	host = '' #localhost
	port = 50007
	myaddr = (host, port)
	server.startHandler(myaddr) #start listening for clients