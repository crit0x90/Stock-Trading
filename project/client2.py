#################################
# Author: Scott McCoy           #
# Course: CSCI 156              #
# Term Project Fall 2017        #
#################################

import sys
import socket
import random
import time
from threading import Thread 

def now():
	return time.ctime(time.time())

class Client():
	def __init__(self, name, host, port, start_state, x, y, z):
		self.name = name
		self.host = host
		self.port = port
		self.state = start_state #buy or sell
		self.balance = 10000000
		self.x = x # % incease to sell
		self.y = y # % decrease to sell
		self.z = z # %buy

		#keeps track of the previous prices for the stocks;
		#important to selling
		self.old_price = {
		'AAPL' : 0.0,
		'GOOG' : 0.0,
		'INTC' : 0.0,
		'RHT'  : 0.0,
		'IBM'  : 0.0,
		'FB'   : 0.0,
		}

		#each client has 10 stocks to start with
		self.stocks = {
		'AAPL' : 10,
		'GOOG' : 10,
		'INTC' : 10,
		'RHT'  : 10,
		'IBM'  : 10,
		'FB'   : 10,
		}

	def chooseStock(self):
		#chooses a random stock from the list
		num = random.randint(1,6)
		if num == 1:
			return 'AAPL'
		elif num == 2:
			return 'GOOG'
		elif num == 3:
			return 'INTC'
		elif num == 4:
			return 'RHT'
		elif num == 5:
			return 'IBM'
		else:
			return 'FB'

	def getNumStocks(self, stock):
		return self.stocks[stock]

	def swapStates(self):
		#this function changes the state of the client because
		#the client is designed to alternate between buying 
		#and selling
		if self.state == 'BUY':
			self.state = 'SELL'
		else:
			self.state = 'BUY'

	def startMonitor(self):
		#this is in charge of printing the status information for the client
		while True:
			print('-------------------------------------------------------------------')
			print(self.name, 'status report')
			print('Time: ', now())
			print('Balance:', self.balance)
			print('Stocks held:')
			print('AAPL - ', self.stocks['AAPL'])
			print('GOOG - ', self.stocks['GOOG'])
			print('INTC - ', self.stocks['INTC'])
			print('RHT  - ', self.stocks['RHT'])
			print('IBM  - ', self.stocks['IBM'])
			print('FB   - ', self.stocks['FB'])
			print('-------------------------------------------------------------------')

			time.sleep(10)

	def processQuery(self, query):
		#queries are in the form 'Action, Stock, Price'
		query = query.split(',')
		price = float(query[2])

		if query[0] == 'BUY':
			#z check
			if random.uniform(0,1) < self.z:
				num_stocks = random.randint(1,10) #pick random stock
				self.balance = self.balance - (num_stocks * price) #update balance
				self.stocks[query[1]] = self.stocks[query[1]] + num_stocks #update number of stocks
				print('$>', self.name, 'is buying', query[1],'!')
			else:
				print('$>', self.name, 'decided not to buy')

		elif query[0] == 'SELL': 
			#if we have more than 0 stocks and price is less than 
			#lower bound or greater than upper bound we sell
			if (self.getNumStocks(query[1]) > 0) and ((price < (self.old_price[query[1]] - (self.y * self.old_price[query[1]]))) or (price > ((self.old_price[query[1]] * self.x) + self.old_price[query[1]]))):
				print('$>', self.name, 'is selling', query[1],'!')
				self.balance = self.balance + (self.getNumStocks(query[1]) * price) #update balance
				self.stocks[query[1]] = 0 #when we sell we sell all
			else:
				print('$>', self.name, 'decided not to sell this round')

		else:
			print('$>', self.name,': Error is processing transation')

		self.old_price[query[1]] = price #updates the old price
		time.sleep(1) #simulates the processing of the transaction

	def connectAndProcess(self):
		#creates a TCP socket and attempts to connect to the server
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.host, self.port))

		#starts up the monitor thread
		thread = Thread(target = self.startMonitor)
		thread.start()

		while True:
			#----------------------------------------------------------
			#client sends 'Name, Action, Stock' (recv buffer 35 bytes)
			stock = self.chooseStock()
			message = self.name + ',' + self.state + ',' + stock
			message = message.encode() #convert message to bytes
			message += b'0' * (35 - len(message)) #appends 0 to message until it meets the required length
			self.s.send(message)
			#----------------------------------------------------------


			#----------------------------------------------------------------------
			#client recieves data in the form 'Status, Stock, Price' (incoming message size 35 bytes)
			data = self.s.recv(35)
			print("$> Client recieved: ", data)
			data = data.decode('utf-8')
			data = data.rstrip('0')
			data = data.split(',')

			if data[0] == 'SUCCESS':
				print('$> Server query successful, processing')
				query = self.state + ',' + data[1] + ',' + data[2]
				self.processQuery(query)

			else:
				print('$> Server query unsuccessful, no processing this round')
			#----------------------------------------------------------------------


			#-----------------------------------------------------
			#client sends 'Ready' when it is ready to proceed
			message = self.name + ' Ready'
			self.s.send(message.encode())
			#-----------------------------------------------------


			#-----------------------------------------------------
			#client recieves 'Proceed' when all other clients are done and the server advances the prices
			data = self.s.recv(7) #incoming message size = 
			print("Client recieved: ", data)
			self.swapStates()
			#-----------------------------------------------------

		thread.join() #exits monitor thread
		print('Monitor exiting')


if __name__ == '__main__':
	name = 'client_2' #do not change the name

	#default data
	serverHost  = 'localhost' #default used for testing
	serverPort = 50007 #default used for testing
	start_state = 'BUY'
	x = 0.1
	y = 0.1
	z = 0.5

	#custom data
	serverHost = input('Enter the IP address of the server: ')
	serverPort = int(input('Enter the port that the server is using: '))
	x = float(input('Enter the x value as a decimal: '))
	y = float(input('Enter the y value as a decimal: '))
	z = float(input('Enter the z value as a decimal: '))

	client1 = Client(name, serverHost, serverPort, start_state, x, y, z)
	client1.connectAndProcess()

	client1.s.close()
