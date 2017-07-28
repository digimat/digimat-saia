#!/usr/bin/python

##############################################################################
# Project: 	MBLogic
# Module: 	mbrtuclient.py
# Purpose: 	ModbusRTU Generic Client.
# Language:	Python 2.6
# Date:		04-Aug-2010.
# Version:	26-Jan-2011.
# Author:	J. Pomares.
# Copyright:	2010 - 2011 - Juan Pomares       	<pomaresj@gmail.com>
# Based on code of Michael Griffin <m.os.griffin@gmail.com>
#
# This file is proposed to be optional part of MBLogic.
# MBLogic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# MBLogic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with MBLogic. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

"""
Implements the Modbus/RTU (serial) client protocol. 

Classes:
MbrtuClient - This is used to create a Modbus/RTU client, based on generic client
framework, running on a timed basis and polls the configured devices. It must be
initialised with a reference to an object containing all the client information
(client connection object). The client connection object contains all the address
and polling information required to operate the client.

Changes were made to file mblogic/mbstatuspages/statuspages/genericparamdata.js, to include new labels.
"""


# Required 
import time
import signal
import GenClientLib
import sys
# Library used to handle serial ports
_serialfailmsg = '\n\nFatal error in mbtuclient.py - Could not import serial library.\n\n'
# Library used to handle serial ports.
# serial is not a standard library. Check to see if it is present. If it is not
# present, we print an error message and then exit.
try:
	import serial
except:
	print(_serialfailmsg)
	sys.exit(38)
# Support libraries for Modbus RTU generic client
import mbrtuconfig
import mbrtumsg


# Indexation for statistics table
statdef = {'present': 0, 'queries': 1, 'valids': 2, 'invalids': 3, 'framerrors': 4,\
	'timeouts': 5, 'retries': 6, 'efficiency': 7}


##############################################################################
class MBRTUClient:
	# Implementation of serial Modbus/RTU client in generic framework


	########################################################
	def __init__(self):
		# Variable definitions
		# Client Name
		self._Name = ''
		# Configuration is OK.
		self._ConfigOK = False
		# Connection status.
		self._ConnectStatus = 'starting'
		# Index of poll status (sending or receiving)
		self._PollStatus = 'sending'
		# Command status.
		self._CmdStatusBuff = []
		# Command list.
		self._CmdList = []
		# Quantity of valid commands for this client
		self._CmdQty = 0
		# Index of current (active) command
		self._CmdIndex = -1
		# Client messages.
		self._ClientMsgs = []
		# Qty of consecutives retries for current command
		self._CmdRetries = 0
		# Steps counters for current command
		self._CmdSteps = -1
		# This formats the command status messages
		self._StatusMsgs = GenClientLib.StatCodes()
		# Qty of coil addresses to be written to the server
		self._WriteCoilSize = 0
		# Qty of discrete input addresses to be written to the server
		self._WriteInpSize = 0
		# Qty of holding register addresses to be written to the server
		self._WriteHoldingregSize = 0
		# Qty of input register addresses to be written to the server
		self._WriteInpregSize = 0
		# Serial Port
		self._PortName = ''
		# Define what are the valid baud rates
		self._ValidBaudRates = ['110', '300', '600', '1200', '2400', '4800', '9600', '14400',
			'19200', '28800', '38400', '56000', '57600', '115200', '128000', '256000']
		# Current Client Baud Rate
		self._BaudRate = 0
		# Parity
		self._Parity = ''
		# Data Bits
		self._ByteSize = 0
		# Stop Bits
		self._StopBits = 0
		# Command Time
		self._CmdTime = 0.0	
		# Repeat Time
		self._RepeatTime = 0.0
		# Retry Time
		self._RetryTime = 0.0
		# Offset for statistics table, inside inpreg group of writetable
		self._StatTable = 0
		# Table of data to be read from the server
		self._ReadTable = {}
		# Table of data to be written to the server
		self._WriteTable = {}
		# Serial Port
		self._SerialPort = serial.Serial()
		# Size (in # of chars) of message to be received from slave
		self._CmdResponseSize = 0
		# Size (in chars) of Modbus error response
		self._CmdErrorSize = 5
		# Qty of consecutive faults allowed to declare a command "faulted"
		self._MaxFaultsAllowed = 5
		# Size of statistical counters for each command
		self._StatRegQty = 10
		# Default time of each cycle in the sending/receiving loop
		self._StepTime = 0.15
		
	########################################################
	def _AddCmdStatus(self, cmd, statcode):
		#Add the status for a command.
		self._CmdStatusBuff.append(self._StatusMsgs.FormatStatusCode(cmd, statcode))
				

	########################################################
	def GetClientMsgs(self):
		#Return the list of client messages.
		return self._ClientMsgs


	########################################################
	def GetStatus(self):
		"""
			Return:
				Connection Status (string) = A code that represents the status of
					the generic client, including the connection to any field
					devices.
				Command Status (dict) = A dictionary containing the latest
					status of any commands. This must be in the format:
					{'cmdname1' : (0, 'noresult', 'No Result'), 
					'cmdname2' : (0, 'ok', 'Ok'), etc. }
				The tuple values have the following meanings:
				1st (integer) - The status code to be written to the data table.
				2nd (string) - A key representing the status description.
				3rd (string) - An optional string representing the status description.
		"""
		cmdstat = self._CmdStatusBuff
		self._CmdStatusBuff = []
		return self._ConnectStatus, cmdstat


	########################################################
	def _InitClient(self):
		"""
			This initialize the Modbus RTU serial generic client
			according to parameters received and validated.
		"""

		# Initialize data table to be written to the server		
		coils = []
		inp = []
		holdingreg = []
		inpreg = []
		# Coils		
		for index in range(0, self._WriteCoilSize):
			coils.append(False)
		self._WriteTable['coil'] = coils
		# Discrete inputs
		for index in range(0, self._WriteInpSize):
			inp.append(False)
		self._WriteTable['inp'] = inp
		# Holding Registers
		for index in range(0, self._WriteHoldingregSize):
			holdingreg.append(0)
		self._WriteTable['holdingreg'] = holdingreg
		# Input registers
		for index in range(0, self._WriteInpregSize):
			inpreg.append(0)
		self._WriteTable['inpreg'] = inpreg
		# Initialize serial port
		self._SerialPort.port = self._PortName
		self._SerialPort.baudrate = self._BaudRate
		self._SerialPort.parity = self._Parity
		self._SerialPort.bytesize = self._ByteSize
		self._SerialPort.stopbits = self._StopBits
		self._SerialPort.timeout = self._RetryTime
		self._SerialPort.xonxoff = False
		self._SerialPort.rtscts = False
		self._SerialPort.dsrdtr = False
		self._SerialPort.interCharTimeout = None
		# Try to open configured serial port, report an error if unsuccesful
		try:
			# Open selected serial port
			self._SerialPort.open()
			# Verify if selected serial port is available
			self._SerialPort.inWaiting()
			self._ClientMsgs.append('Serial port %s opened.' % self._PortName)
			self._ConfigOK = True
		except:
			self._ClientMsgs.append('Could not open serial port %s.' % self._PortName)
			# Set the connection status.
			self._ConnectStatus = 'faulted'


	########################################################
	def SetParams(self, hostconfig, clientconfig, cmdlist):
		"""
			This must accept the configuration parameters
			dictionary and validate the parameters in it. 
			Parameters: 
				hostconfig (dict) = The standard configuration parameters 
					used by the server. The generic client does not 
					typically need to use this information.
				clientconfig (dict) = These are the parameters intended 
					for the generic client and must be validated by 
					the client.
				cmdlist (dict) = A list of commands for the client. These 
					must be validated by the client (if there are any).
		"""

		# List of valid data types.
		DataTypes = ['coil', 'inp', 'holdingreg', 'inpreg']
		# List of faults detected
		faulterrs = []
		
		# Validate the expected Host parameters.
		# Client Name		
		self._Name = hostconfig['connectionname']
		# Read size for each data type in writetable
		writetable = hostconfig['writetable']
		# Qty of coil addresses to be written to the server
		try:
			writesize = writetable['coil']
			self._WriteCoilSize = int(writesize[1])
		except: pass
		# Qty of discrete input addresses to be written to the server
		try:
			writesize = writetable['inp']
			self._WriteInpSize = int(writesize[1])
		except: pass
		# Qty of holding register addresses to be written to the server
		try:
			writesize = writetable['holdingreg']
			self._WriteHoldingregSize = int(writesize[1])
		except: pass
		# Qty of input register addresses to be written to the server
		try:
			writesize = writetable['inpreg']
			self._WriteInpregSize = int(writesize[1])
		except: pass
			
		# Validate the expected Client parameters.
		# Serial Port name.
		try:
			serialport = clientconfig['serialport']
			if (len(serialport) < 1):
				faulterrs.append('Invalid serial port name (/dev/tty...): %s.' % clientconfig['serialport'])			
			else:
				self._PortName = serialport
		except:
			faulterrs.append('Missing serial port name (/dev/tty...).')
		# Baud Rate
		try:
			baudrate = clientconfig['baudrate']
			validparameter = False
			for index in self._ValidBaudRates:
				if (index == baudrate):
					self._BaudRate = int(baudrate)
					validparameter = True
			# If parameter baudrate is invalid, report an error
			if not(validparameter):
				faulterrs.append('Invalid baud rate (110-256000): %s.' % clientconfig['baudrate'])
		except:
			faulterrs.append('Missing baud rate (110-256000).')
		# Parity
		try:
			parity = clientconfig['parity']
			value = parity.lower()
			if (value == 'e' or value == 'even'):
				self._Parity = serial.PARITY_EVEN
			elif (value == 'o' or value == 'odd'):
				self._Parity = serial.PARITY_ODD
			elif (value == 'm' or value == 'mark'):
				self._Parity = serial.PARITY_MARK
			elif (value == 's' or value == 'space'):
				self._Parity = serial.PARITY_SPACE
			elif (value == 'n' or value == 'none'):
				self._Parity = serial.PARITY_NONE
			# If parameter parity is invalid, report an error
			else:
				faulterrs.append('Invalid parity (e,o,m,s,n): %s.' % clientconfig['parity'])
		except:
			faulterrs.append('Missing parity (e,o,m,s,n).')
		# Qty of Data Bits
		try:
			bytesize = clientconfig['bytesize']
			if (bytesize == '7'):
				self._ByteSize = serial.SEVENBITS				
			elif (bytesize == '8'):
				self._ByteSize = serial.EIGHTBITS
			else:
				faulterrs.append('Invalid byte size (7,8): %s.' % clientconfig['bytesize'])
		except:
			faulterrs.append('Missing byte size (7,8).')
		# Qty of Stop Bits
		try:
			stopbits = clientconfig['stopbits']
			if (stopbits == '1'):
				self._StopBits = serial.STOPBITS_ONE
			elif (stopbits == '2'):
				self._StopBits = serial.STOPBITS_TWO
			else:
				faulterrs.append('Invalid stop bits (1,2): %s.' % clientconfig['stopbits'])
		except:
			faulterrs.append('Missing stop bits (1,2).')
		# Maximum Retries allowed
		try:
			retries = int(clientconfig['retries'])
			if (retries < 0):
				faulterrs.append('Invalid retries: %s.' % clientconfig['retries'])				
		except:
			faulterrs.append('Missing or invalid retries (0,1,2,...).')
		# Command Time
		try:
			cmdtime = int(clientconfig['cmdtime']) / 1000.0
			if (cmdtime < 0):
				faulterrs.append('Invalid command time (msec): %s.' % clientconfig['cmdtime'])				
		except:
			faulterrs.append('Missing or invalid command time (msec).')
		# Repeat Time
		try:
			repeattime = int(clientconfig['repeattime']) / 1000.0
			if (repeattime < 0):
				faulterrs.append('Invalid repeat time (msec): %s.' % clientconfig['repeattime'])			
		except:
			faulterrs.append('Missing or invalid repeat time (msec).')
		# Retry Time
		try:
			retrytime = int(clientconfig['retrytime']) / 1000.0
			if (retrytime < 0):
				faulterrs.append('Invalid retry time (msec): %s.' % clientconfig['retrytime'])			
		except:
			faulterrs.append('Missing or invalid retry time (msec).')

		# Validate the client commands.
		validator = mbrtuconfig.MBRTUCommandConfig()
		self._CmdList, errorlist = validator.CheckMBRTUClientCmd(cmdlist, hostconfig)
		# Calculate qty of valid commands		
		self._CmdQty = len(self._CmdList)
		# Validate if there is, at least, one valid command		
		if (self._CmdQty == 0):
			faulterrs.append('There are not valid commands for this client.')		
		# Pass errorlist list from command validation to client messages list
		self._ClientMsgs.extend(errorlist)
		
		# Validate statistics table space availability, based on qty of valid commands
		try:
			# Command's statistical table index/offset (inside inpreg group of writetable)
			statisticstable = int(clientconfig['statisticstable'])
		except:
			statisticstable = 0
			faulterrs.append('Missing or invalid statistical table input register offset (inpregs).')			
		# Validate if statistics table is out of range, with respect to input registers in writetable
		if ((statisticstable + (self._CmdQty * self._StatRegQty)) > self._WriteInpregSize) \
			or (statisticstable < 0):
				faulterrs.append('Statistical table out of range inside input registers, offset: %s + size: %s' \
				% (statisticstable, (self._CmdQty * self._StatRegQty)))	

		# If no critical errors where found, complete remaining fields of class
		if (len(faulterrs) == 0 and self._CmdQty > 0):
			self._Retries = retries
			self._CommandTime = cmdtime
			self._RepeatTime = repeattime
			self._RetryTime = retrytime
			self._StatTable = statisticstable
			# Notify that client configuration is ok.
			self._ClientMsgs.append('The client parameters were ok.')
			# Initialize the Modbus RTU client with received parameters.
			self._InitClient()
		else:
			# Set the connection status.
			self._ConnectStatus = 'faulted'
			# Save the errors.
			self._ClientMsgs.extend(faulterrs)


	########################################################
	def NextCommand(self, readtable, servercmd):
		"""
			This should execute the next command, whatever it is. This
			is called regularly by GenClient.
			Parameters:
				readtable (dict) = A dictionary containing a mirror of the
					requested portion of the server data table. E.g.
					{'coil' : [True, False, True, True], 'inp' : [True, False, True, True],
					'inpreg' : [], 'holdingreg' : [1234, 5678]}
				servercmd (string) = A command from the server. This will 
					consist of one of the following:
					'run' = Run normally.
					'stop' = Stop operation.
					'pause' = Pause operation.
					'restart' = A restart is requested. The restart 
						request will remain in effect until new
						parameters are loaded. This is not implemented in this version.
			Returns: 
				writetable (dict) = A dictionary in the same format as the "readtable" input parameter.
					This will contain the data to be written to the server. Data table items in excess 
					of those configured for transfer will be ignored.
				nextpoll (float) = The time in seconds to wait before running this function again.
		"""

		# Set default time for next poll
		nextpoll = self._StepTime

		# If client is configured and server command is "run", report it as "running"
		if (self._ConfigOK == True and servercmd == 'run'):
			self._ConnectStatus = 'running'
		# If client is configured and server command is "stop", report it as "stopped"
		if (self._ConfigOK == True and servercmd == 'stop'):
			self._ConnectStatus = 'stopped'
		# If client is configured and server command is "pause", report it as "paused"
		if (self._ConfigOK == True and servercmd == 'pause'):
			self._ConnectStatus = 'paused'

		# If client is running, send/receive data
		if (self._ConnectStatus == 'running'):
			# Send the next message
			if (self._PollStatus == 'sending'):
				self._CmdIndex += 1
				if (self._CmdIndex >= self._CmdQty):
					self._CmdIndex = 0
				# If action is not disabled, execute this command
				if (self._CmdList[self._CmdIndex]['action'] != 'disabled'):
					# Get the data to be send.
					if (self._CmdList[self._CmdIndex]['function'] in [5, 6, 15, 16]):
						data2send = readtable[self._CmdList[self._CmdIndex]['datatype']] \
							[self._CmdList[self._CmdIndex]['dataoffset']: \
							(self._CmdList[self._CmdIndex]['dataoffset']+self._CmdList[self._CmdIndex]['qty'])]
					else:
						data2send = None
					# Get the next command in the list.
					RequestMsg, self._CmdResponseSize = mbrtumsg.MBRTURequest(self._CmdList[self._CmdIndex]['uid'], \
						self._CmdList[self._CmdIndex]['function'], self._CmdList[self._CmdIndex]['remoteaddr'], \
						self._CmdList[self._CmdIndex]['qty'], data2send)
					""" If action is 'oneshot', evaluate if the current command is 'Read' type and was 
					successfully sent previously, or if the current command is 'Write' type and data
					to send as not changed since last succesfully scan.
					If that is not the case, send the command and change the state to 'receiving'
					"""
					if not ((self._CmdList[self._CmdIndex]['action'] == 'oneshot' and \
						self._CmdList[self._CmdIndex]['sent']) and \
						( (self._CmdList[self._CmdIndex]['function'] in [1, 2, 3, 4]) or
						( (self._CmdList[self._CmdIndex]['function'] in [5, 6, 15, 16]) and \
						RequestMsg == self._CmdList[self._CmdIndex]['msgcache'] ) ) ):
						# Clear output buffer, aborting the current output and discarding all that is in the buffer.
						self._SerialPort.flushOutput()
						# Flush input buffer, discarding all it's contents.
						self._SerialPort.flushInput()
						# Send the message through the serial port.
						self._SerialPort.write(RequestMsg)
						# Save the current command as the last valid command sent.
						self._CmdList[self._CmdIndex]['msgcache'] = RequestMsg
						# Update statistics registers for this command
						self._WriteTable['inpreg'][self._StatTable + (self._CmdIndex * self._StatRegQty) + statdef['queries']] += 1
						# Change the state of loop
						self._PollStatus = 'receiving'
						# Initialize the counters of steps and retries				
						self._CmdSteps = -1
						self._CmdRetries = 0
			# Wait for response of slave (server) and process it
			elif (self._PollStatus == 'receiving'):
				# Increases the steps counter for this command.
				self._CmdSteps += 1
				# Index for statistics table updates
				cmdstatindex = self._StatTable + (self._CmdIndex * self._StatRegQty)

				# Evaluate if size of received message is the expected (normal or error)
				if (self._SerialPort.inWaiting() in [self._CmdErrorSize, self._CmdResponseSize]):
					ReplyMsg = self._SerialPort.read(self._SerialPort.inWaiting())
					# Decode received modbus message
					unitid, functioncode, datareceived, exception = mbrtumsg.MBRTUResponse(ReplyMsg)
					# Update statistics registers for this command
					# No errors
					if (exception == 0):
						self._WriteTable['inpreg'][cmdstatindex + statdef['present']] = 1
						self._WriteTable['inpreg'][cmdstatindex + statdef['valids']] += 1
						# Set the command status ok.
						self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'ok')
						# If last command, wait 'Repeat Time', but wait 'Command Time'
						if ((self._CmdIndex + 1) == self._CmdQty):
							nextpoll = self._RepeatTime
						else:
							nextpoll = self._CommandTime
						# Change the state of loop
						self._PollStatus = 'sending'
					else:
						# Increment retries counter
						self._CmdRetries += 1
						# Received modbus frame with bad checksum or unexpected size/format
						if (exception == 8):
							self._WriteTable['inpreg'][cmdstatindex + statdef['framerrors']] += 1
						# Other errors
						else:
							self._WriteTable['inpreg'][cmdstatindex + statdef['invalids']] += 1
						""" If command is 'dead' then there is no retries for this command,
						for optimization in the use of limited serial channel capacity
						"""
						if (self._CmdList[self._CmdIndex]['faults'] == self._MaxFaultsAllowed):
							# Notify that command is faulted and has no results.
							self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'noresult')
							# Increment command fault counter to prevent useless error messages
							self._CmdList[self._CmdIndex]['faults'] += 1
						if (self._CmdList[self._CmdIndex]['faults'] > self._MaxFaultsAllowed):
							# If last command, wait 'Repeat Time'
							if ((self._CmdIndex + 1) == self._CmdQty):
								nextpoll = self._RepeatTime
							# Change the state of loop
							self._PollStatus = 'sending'
						else:
							# Check if max retries is reached, so an error is declared
							if (self._CmdRetries > self._Retries):
								# Increment the consecutive fault register for current command
								self._CmdList[self._CmdIndex]['faults'] += 1
								# Update statistics registers for this command
								self._WriteTable['inpreg'][cmdstatindex + statdef['present']] = 0
								# Set the command status.
								if (exception == 1):
									self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'badfunc')
								elif (exception == 2):
									self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'badaddr')
								elif (exception == 3):
									self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'badqty')
								elif (exception == 4):
									self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'deviceerr')
								elif (exception == 8):
									self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'frameerr')
								else:
									self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'servererr')
								# If last command, wait 'Repeat Time'
								if ((self._CmdIndex + 1) == self._CmdQty):
									nextpoll = self._RepeatTime
								# Change the state of loop
								self._PollStatus = 'sending'
							# Try again the current command
							else:
								# Update statistics registers for this command
								self._WriteTable['inpreg'][cmdstatindex + statdef['retries']] += 1
								self._CmdSteps = -1
								self._SerialPort.flushOutput()
								# Flush input buffer, discarding all it's contents.
								self._SerialPort.flushInput()
								# Get the data to be send.
								if (self._CmdList[self._CmdIndex]['function'] in [5, 6, 15, 16]):
									data2send = readtable[self._CmdList[self._CmdIndex]['datatype']] \
										[self._CmdList[self._CmdIndex]['dataoffset']: \
										(self._CmdList[self._CmdIndex]['dataoffset']+self._CmdList[self._CmdIndex]['qty'])]
								else:
									data2send = None
								# Construct modbus message.
								RequestMsg, self._CmdResponseSize = mbrtumsg.MBRTURequest(self._CmdList[self._CmdIndex]['uid'], \
									self._CmdList[self._CmdIndex]['function'], self._CmdList[self._CmdIndex]['remoteaddr'], \
									self._CmdList[self._CmdIndex]['qty'], data2send)
								self._SerialPort.write(RequestMsg)
					# If received message is ok, update writetable
					if (exception == 0):
						# Set the flag of successfully sent command
						self._CmdList[self._CmdIndex]['sent'] = True
						# Clear the consecutive fault register for current command
						self._CmdList[self._CmdIndex]['faults'] = 0
						# If command is 1, 2, 3 or 4, update data in writetable
						if (self._CmdList[self._CmdIndex]['function'] in [1, 2, 3, 4]):
							# Write to discrete inputs and coils
							if (self._CmdList[self._CmdIndex]['datatype'] in ['coil', 'inp']):
								dataindex = 0
								for tableindex in range(self._CmdList[self._CmdIndex]['dataoffset'], \
									(self._CmdList[self._CmdIndex]['dataoffset'] + self._CmdList[self._CmdIndex]['qty'])):
									if (datareceived[dataindex] == True or datareceived[dataindex] > 0):
										self._WriteTable[self._CmdList[self._CmdIndex]['datatype']][tableindex] = True
									dataindex += 1
							# Write to 16-bits word registers							
							elif (self._CmdList[self._CmdIndex]['datatype'] in ['holdingreg', 'inpreg']):
								dataindex = 0
								for tableindex in range(self._CmdList[self._CmdIndex]['dataoffset'], \
									(self._CmdList[self._CmdIndex]['dataoffset'] + self._CmdList[self._CmdIndex]['qty'])):
									try:
										# Validate if data is integer
										receiveddata = int(datareceived[dataindex])
										# Generic server handle signed data (-32767 to +32767
										if (receiveddata > 32767):
											sigintdata = receiveddata - 65535
										else:
											sigintdata = receiveddata
										self._WriteTable[self._CmdList[self._CmdIndex]['datatype']][tableindex] = sigintdata
									except:
										if (datareceived[dataindex] == True):
											self._WriteTable[self._CmdList[self._CmdIndex]['datatype']][tableindex] = 1
										else:
											self._WriteTable[self._CmdList[self._CmdIndex]['datatype']][tableindex] = 0										
									dataindex += 1
							else:
								pass
				# Check if Retry Time (timeout) is reached
				elif ((self._CmdSteps * self._StepTime) >= self._RetryTime):
					# Update statistics registers for this command
					self._WriteTable['inpreg'][cmdstatindex + statdef['timeouts']] += 1
					# Increment retries counter
					self._CmdRetries += 1
					""" If command is 'dead' then there is no retries for this command,
					for optimization in the use of limited serial channel capacity
					"""
					if (self._CmdList[self._CmdIndex]['faults'] == self._MaxFaultsAllowed):
						# Notify that command is faulted and has no results.
						self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'noresult')
						# Increment command fault counter to prevent useless error messages 
						self._CmdList[self._CmdIndex]['faults'] += 1
					if (self._CmdList[self._CmdIndex]['faults'] > self._MaxFaultsAllowed):
						# Update statistics registers for this command
						self._WriteTable['inpreg'][cmdstatindex + statdef['present']] = 0
						# If last command, wait 'Repeat Time'
						if ((self._CmdIndex + 1) == self._CmdQty):
							nextpoll = self._RepeatTime
						# Change the state of loop
						self._PollStatus = 'sending'
					# Check is max retries is reached, so a fault is declared
					elif (self._CmdRetries > self._Retries):
						# Increment the consecutive fault register for current command
						self._CmdList[self._CmdIndex]['faults'] += 1
						# Update statistics registers for this command
						self._WriteTable['inpreg'][cmdstatindex + statdef['present']] = 0
						# Set the command status.
						self._AddCmdStatus(self._CmdList[self._CmdIndex]['command'], 'timeout')
						# If last command, wait 'Repeat Time'
						if ((self._CmdIndex + 1) == self._CmdQty):
							nextpoll = self._RepeatTime
						# Change the state of loop
						self._PollStatus = 'sending'
					# Try again the current command
					else:
						# Update statistics registers for this command
						self._WriteTable['inpreg'][cmdstatindex + statdef['retries']] += 1
						self._CmdSteps = -1
						self._SerialPort.flushOutput()
						# Flush input buffer, discarding all it's contents.
						self._SerialPort.flushInput()
						# Get the data to be send.
						if (self._CmdList[self._CmdIndex]['function'] in [5, 6, 15, 16]):
							data2send = readtable[self._CmdList[self._CmdIndex]['datatype']] \
								[self._CmdList[self._CmdIndex]['dataoffset']: \
								(self._CmdList[self._CmdIndex]['dataoffset']+self._CmdList[self._CmdIndex]['qty'])]
						else:
							data2send = None
						# Construct modbus message.
						RequestMsg, self._CmdResponseSize = mbrtumsg.MBRTURequest(self._CmdList[self._CmdIndex]['uid'], \
							self._CmdList[self._CmdIndex]['function'], self._CmdList[self._CmdIndex]['remoteaddr'], \
							self._CmdList[self._CmdIndex]['qty'], data2send)
						self._SerialPort.write(RequestMsg)
				# Wait for the next step
				else:				
					pass

				""" Generic server handle signed data (-32767 to +32767, so validate 
				if any register of statistics table for this command exceed that limit : 32767
				"""
				# Index for statistics table updates
				cmdstatindex = self._StatTable + (self._CmdIndex * self._StatRegQty)
				for index in range(cmdstatindex, (cmdstatindex + self._StatRegQty - 1)):
					if (self._WriteTable['inpreg'][index] > 32767):
						# Reset statistics registers for this command
						self._WriteTable['inpreg'][cmdstatindex + statdef['queries']] = 0
						self._WriteTable['inpreg'][cmdstatindex + statdef['valids']] = 0							
						self._WriteTable['inpreg'][cmdstatindex + statdef['invalids']] = 0			
						self._WriteTable['inpreg'][cmdstatindex + statdef['framerrors']] = 0	
						self._WriteTable['inpreg'][cmdstatindex + statdef['timeouts']] = 0
						self._WriteTable['inpreg'][cmdstatindex + statdef['retries']] = 0

				# Calculate efficiency for this command, efficiency = valid/queries
				if (self._WriteTable['inpreg'][cmdstatindex + statdef['queries']] > 0): 
					self._WriteTable['inpreg'][cmdstatindex + statdef['efficiency']] = \
						int(self._WriteTable['inpreg'][cmdstatindex + statdef['valids']] \
						* 100 / self._WriteTable['inpreg'][cmdstatindex + statdef['queries']])

		return self._WriteTable, nextpoll


##############################################################################
# Signal handler.
def SigHandler(signum, frame):
	print('Operator terminated Modbus RTU client %s at %s' % (clientname, time.ctime()))
	mbrtucontrol.StopClient()

def SigTermHandler(signum, frame):
	print('Received terminate signal for Modbus RTU client %s at %s' % (clientname, time.ctime()))
	mbrtucontrol.StopClient()


##############################################################################

# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)
signal.signal(signal.SIGTERM, SigTermHandler)

# Get the command line parameter options.
CmdOpts = GenClientLib.GetOptions()
port, clientname, startdelay = CmdOpts.GetStartParams()

# Initialise the Modbus RTU client handler.
mbrtucontrol = GenClientLib.GenClientController(port, clientname, MBRTUClient)

print('Starting Modbus RTU client %s at %s' % (clientname, time.ctime()))

# Delay the specified number of seconds. This will allow the main
# program to start up before trying to contact it.
time.sleep(startdelay)

# Start the generic client.
mbrtucontrol.StartClient()

print('Modbus RTU client %s halted at %s' % (clientname, time.ctime()))
