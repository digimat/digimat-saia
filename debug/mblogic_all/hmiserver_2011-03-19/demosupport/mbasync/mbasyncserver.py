#!/usr/bin/python
##############################################################################
# Project: 	mbasyncserver
# Module: 	mbasyncserver.py
# Purpose: 	Modbus TCP Server (slave).
# Language:	Python 2.5
# Date:		08-Mar-2008.
# Ver:		24-Sep-2009.
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of MBAsyncServer.
# MBAsyncServer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# MBAsyncServer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with MBAsyncServer. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

_HelpStr = """
===========================================================
MBAsyncServer Ver. 24-Sep-2009

This program provides a simple asynchronous Modbus TCP server (slave). 
It supports Modbus functions 1, 2, 3, 4, 5, 6, 15, and 16. This is strictly 
a passive server and offers no client (master) functionality. 

The server contains a Modbus memory map which is defined as follows:
Coils, Discrete Inputs, Holding Registers, and Input Registers are defined 
for their full address range (0 to 65535). Coils and Discrete Inputs share
the same address space. Holding Registers, and Input Registers also share
the same address space. This means that writing to a Coil also affects the 
corresponding Discrete Input, and writing to a Holding Register affects the 
corresponding Input Register.

There is also an option to pack the Coils and Discrete Inputs into the first 
4096 registers (16 coils per register). When this option is enabled, writing 
to a Coil or Discrete Input affects the corresponding register, and visa versa.
When the Coils and Discretes Inputs are *not* packed into registers, this 
called a separate data table. When they are packed into registers, this is
called an overlaid data table. The default is 'separate'.
E.g. "python mbasyncserver.py -d s".

The server listens on port 502 by default. This may be changed to any other 
port number through the use of the "-p" command line parameter. 
E.g. "python mbasyncserver.py -p 8080".

As well as the normal Modbus commands, the server can also be made to 
respond to a special shut down signal which causes the program to exit. 
This is sometimes useful when testing clients, especially when running 
multiple servers. The shut down signal is defined by the "-q" parameter. 
E.g. "python mbasyncserver.py -q quit". Simply send the shut down command
to the server on the same port which it is listening to Modbus commands on, 
and it will exit immediately. If no shutdown command is specified, the 
feature is disabled by default.

Options:
-p - port. E.g. -p 8080
-q - quit command. E.g. -q quit
-d - data table options. s = separate. o = overlay. E.g. -d s
-e - Print help and exit.

Author: Michael Griffin
Copyright 2008 - 2009 Michael Griffin. This is free software. You may 
redistribute copies of it under the terms of the GNU General Public License
<http://www.gnu.org/licenses/gpl.html>. There is NO WARRANTY, to the
extent permitted by law.

"""

############################################################

import getopt, sys
import signal
import time

import asyncore
import socket

from mbprotocols import ModbusTCPMsg
from mbprotocols import ModbusMemTable
from mbprotocols import ModbusDataStrLib

############################################################

SoftwareVersion = '2.01'

############################################################
# Get the command line options.
# The only option is the port number. This may be
# set by the user on the command line. If the user does
# not set any options, then default values are returned.
#
class GetOptions:

	########################################################
	def __init__(self):
		self._port = 502
		self._quit = None
		self._datatableoverlay = False

		# Read the command line options.
		try:
			opts, args = getopt.getopt(sys.argv[1:], 'p: d: q: e:', 
				['port', 'datatable', 'quit', 'help'])
		except:
			print(_HelpStr)
			sys.exit()

		# Parse out the options.
		for o, a in opts:
			# Port number.
			if o == '-p':
				try:
					self._port = int(a)
				except:
					print('Invalid port number.')
					sys.exit()

			# Data table layout.
			elif o == '-d':
				if (a in ['o', 'O']):	# Coils overlaid on registers.
					self._datatableoverlay = True
				elif (a in ['s', 'S']):	# Coils separate from registers.
					self._datatableoverlay = False
				else:
					print('Invalid data table configuration option.')
					sys.exit()

			# Quit command.
			elif o == '-q':
				self._quit = a

			# Print help.
			elif o == '-e':
				print(_HelpStr)
				sys.exit()

			else:
				print('Unrecognised option %s %s' % (o, a))
				sys.exit()

	########################################################
	def GetPort(self):
		"""Return the port setting.
		"""
		return self._port

	########################################################
	def GetQuit(self):
		"""Return the "quit" (shutdown) command. If no command was 
		specified, None is returned, which disables remote shut down. 
		"""
		return self._quit

	########################################################
	def GetDataTableConfig(self):
		"""Returns True if the data table is to use an overlay, 
		False otherwise.
		"""
		return self._datatableoverlay

############################################################



############################################################

# This listens for new connection requests, and when
# a new connection is made it starts up a handler for it
# to run asynchronously.
class AsyncServer(asyncore.dispatcher):

	########################################################
	def __init__(self, port):
		try:
			asyncore.dispatcher.__init__(self)
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		except:
			print('Failed to create socket for port: %d. Exiting...' % port)
			sys.exit()

		# If we exit and then try to restart the server again immediately,
		# sometimes we cannot bind to the port until a short period of time
		# has passed. In this case, we will sleep, and try again later. If
		# we still don't succeed after several attempts, we will give up.
		bindcount = 10
		while True:
			try:
				self.bind(('', port))
				break	# Succeeded, so we can exit this loop.
			except:
				if (bindcount > 0):
					print('Failed to bind to socket for port: %d. Will retry in 30 seconds...' % port)
					bindcount -= 1
					time.sleep(30)
				else:
					print('Failed to bind to socket for port: %d. Exiting...' % port)
					sys.exit()

			
		# Try listening to port.
		try:
			self.listen(5)
		except:
			print('Failed listening to port: %d. Exiting...' % port)
			sys.exit()

		print('Server running...')

	########################################################
	def __del__(self):
		self.close()

	########################################################
	def handle_accept(self):
		NewSocket, Address = self.accept()
		print('Connected from %s  %d' % Address)
		SocketHandler(NewSocket)

############################################################
# An instance of this class is started up for each connection.
class SocketHandler(asyncore.dispatcher_with_send):

	########################################################
	def handle_read(self):

		try:
			ReceivedData = self.recv(8192)
		except:
			ReceivedData = None

		if ReceivedData: 

			if ShutDownCommand and (ReceivedData == ShutDownCommand):
				print('Shutdown command received by server %d. %s' % (CmdOpts.GetPort(), time.ctime()))
				self.close()
				raise asyncore.ExitNow

			# Decode message. 'RequestData' may mean either number of coils or sent data, depending
			# upon the function code being received. For functions 15 and 16, it is a tuple containing
			# data and quantity.
			try:
				TransID, UnitID, FunctionCode, Start, RequestData, ExceptionCode = \
					MBServerMSg.MBRequest(ReceivedData)
			except:
				FunctionCode = 0
				TransID = 0
				UnitID = 0
				Start = 0

			ReplyData = ''
			# Decode messages. If we get an error in reading/writing memory or in constructing messages,
			# we will consider this to be a Modbus exception.
			try:
				if FunctionCode == 1:		# Read coils.	RequestData = quantity.
					MsgData = MemMap.GetCoils(Start, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 2:		# Read discrete inputs.	RequestData = quantity.
					MsgData = MemMap.GetDiscreteInputs(Start, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 3:		# Read holding registers. RequestData = quantity.
					MsgData = MemMap.GetHoldingRegisters(Start, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 4:		# Read input registers.	RequestData = quantity.
					MsgData = MemMap.GetInputRegisters(Start, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, MsgData)

				elif FunctionCode == 5:		# Write single coil. RequestData contains data.
					MemMap.SetCoils(Start, 1, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, RequestData)

				elif FunctionCode == 6:		# Write single holding register. RequestData contains data.
					MemMap.SetHoldingRegisters(Start, 1, RequestData)
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, Start, RequestData)

				elif FunctionCode == 15:	# Write multiple coils.	RequestData is a tuple.
					MemMap.SetCoils(Start, RequestData[0], RequestData[1])
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, \
						Start, ModbusDataStrLib.Int2BinStr(RequestData[0]))

				elif FunctionCode == 16:	# Write multiple holding registers. RequestData is a tuple.
					MemMap.SetHoldingRegisters(Start, RequestData[0], RequestData[1])
					ReplyData = MBServerMSg.MBResponse(TransID, UnitID, FunctionCode, \
						Start, ModbusDataStrLib.Int2BinStr(RequestData[0]))

				elif FunctionCode > 127:	# Modbus exception.
					ReplyData = MBServerMSg.MBErrorResponse(TransID, UnitID, FunctionCode, ExceptionCode)
				else:
					print('Server %d - Unsupported function call' % CmdOpts.GetPort())
					ReplyData = MBServerMSg.MBErrorResponse(TransID, UnitID, FunctionCode + 128, 1)

			except:
				# Modbus exception 4. An error has occured in reading or writing a memory location.
				ReplyData = MBServerMSg.MBErrorResponse(TransID, UnitID, FunctionCode + 128, 4)

			# Send the reply.
			try:
				self.send(ReplyData)
			except:
				# If we have an error here, there's not much we can do about it.
				print('Server %d - Could not reply to request.' % CmdOpts.GetPort())

		else: 
			self.close()

	########################################################
	def handle_close(self):
		try:
			peername = self.getpeername()
		except:
			peername = ('unknown peer', 0)
		print('Disconnected from %s  %d' % peername)


############################################################



# Signal handler.
def SigHandler(signum, frame):
	print('Operator terminated server at %s' % time.ctime())
	sys.exit()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)


# Get the command line parameter options.
CmdOpts = GetOptions()

############################################################

# Initialise a memory data table to hold the data.
# This uses a unified address space for all data types.
# Overlaying coils and registers is optional.
MemMap = ModbusMemTable.ModbusMemTable(unified = True, overlay = CmdOpts.GetDataTableConfig())

# Get the special remote shut down command.
ShutDownCommand = CmdOpts.GetQuit()

maxcoils, maxdiscretes, maxholdingreg, maxinputreg = MemMap.GetMaxAddresses()
MBServerMSg = ModbusTCPMsg.MBTCPServerMessages(maxcoils, maxdiscretes, maxholdingreg, maxinputreg)

print('\n\nMBAsyncServer version %s' % SoftwareVersion)
print('Starting server on port %d. %s' % (CmdOpts.GetPort(), time.ctime()))

# Initialise the main server using the selected port.
AsyncServer(CmdOpts.GetPort())


# Start the server listening. This runs forever.
try:
	asyncore.loop()
except:
	pass

############################################################


