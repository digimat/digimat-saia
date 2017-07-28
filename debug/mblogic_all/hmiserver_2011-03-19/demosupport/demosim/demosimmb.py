#!/usr/bin/python
##############################################################################
# Project: 	HMIServer
# Module: 	demosim.py
# Purpose: 	Simulate a tank process for the HMI demo.
# Language:	Python 2.5
# Date:		26-Feb-2009.
# Ver:		14-Mar-2011.
# Author:	M. Griffin.
# Copyright:	2009 - 2011 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of HMIServer.
# HMIServer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# HMIServer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with HMIDevServer. If not, see <http://www.gnu.org/licenses/>.
#
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

"""
This is a very simple program that simulates the 'tank' demo process for the 
HMI. This is a very unsophisticated program, and not useful for any other 
purpose.
"""

############################################################

import sys
import signal
import time
import random

from mbprotocols import ModbusTCPSimpleClient2
from mbprotocols import ModbusDataLib

############################################################

print('\nStarting the demosim 2.0 at %s' % time.ctime())

# Signal handler.
def SigHandler(signum, frame):
	print('Operator terminated demosim at %s\n' % time.ctime())
	sys.exit()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)

############################################################

servport = 8600

# If the server is not ready, we back off and try again later.
contactcount = 10
servercontacted = False
while not servercontacted:
	try:
		client = ModbusTCPSimpleClient2.ModbusTCPSimpleClient('localhost', servport, 5.0)
		servercontacted = True
	except:
		if (contactcount > 0):
			print('Demosim - could not contact the server at port %s. Will retry in 30 seconds...' % servport)
			contactcount -= 1
			time.sleep(30)
		else:
			print('Demosim - could not contact the server at port %s. Exiting...' % servport)
			sys.exit()



def ContactServer():
	client.SendRequest(1, 1, 1, 0, 1)
	TransID, rfunct, Address, Qty, MsgData, Excode = client.ReceiveResponse()
	
# Now, check to see if we can actually talk to the server.
responseok = False
contactcount = 10
while not responseok:
	try:
		ContactServer()
		responseok = True
	except:
		if (contactcount > 0):
			print('Demosim - could not contact the server at port %s. Will retry in 30 seconds...' % servport)
			contactcount -= 1
			time.sleep(30)
		else:
			print('Demosim - could not contact the server at port %s. Exiting...' % servport)
			sys.exit()
		

############################################################

def GetServerData(func, adr, qty):
	try:
		# Send the request.
		client.SendRequest(1, 1, func, adr, qty)
		# Get the reply.
		TransID, rfunct, Address, Qty, MsgData, Excode = client.ReceiveResponse()
	except:
		print('Demosim - lost contact with server - exiting')
		sys.exit()

	# Decode the data.
	if (rfunct in [1, 2]):
		values = ModbusDataLib.bin2boollist(MsgData)
	elif (rfunct in [3, 4]):
		values = ModbusDataLib.signedbin2intlist(MsgData)
	else:
		print('Demosim - Bad function code %s when reading data.' % rfunct)
		# Provide a default based on the sending function.
		if (func in [1, 2]):
			values = [False] * 8
		elif (funct in [3, 4]):
			values = [0] * 8
	return values

def WriteServerData(func, adr, qty, data):
	if (func == 15):
		msgdata = ModbusDataLib.boollist2bin(data)
	elif (func == 16):
		msgdata = ModbusDataLib.signedintlist2bin(data)
	else:
		print('Demosim - Bad function code %s when writing data.' % func)
		return

	try:
		# Send the request.
		client.SendRequest(1, 1, func, adr, qty, msgdata)
		# Get the reply.
		TransID, rfunct, Address, Qty, MsgData, Excode = client.ReceiveResponse()
	except:
		print('Demosim - lost contact with server - exiting')
		sys.exit()

############################################################

LoopCount = 0

# Loop forever.
while True:
	# Read the push button coils.
	pbcoilvalues = GetServerData(1, 0, 8)
	# Read the push button, tank, and pump holding registers.
	regreadvalues = GetServerData(3, 5000, 8)

	# Read the multi-value push button.
	PBFour = regreadvalues[0]


	# Read the pump speed command.
	pumpflow = regreadvalues[4]


	# Read the tank 1 level.
	tank1level = regreadvalues[2]
	# Read the tank 2 level.
	tank2level = regreadvalues[3]

	# Calculate the new tank level.
	LoopCount += 1
	if LoopCount > 4:
		tank1level = tank1level - pumpflow
		LoopCount = 0

	if tank1level > 95:
		tank1level = 95
		pumpflow = 0
	elif tank1level < 5:
		tank1level = 5
		pumpflow = 0

	tank2level = 100 - tank1level


	# Pilot lights.
	"""
	plvalues = [0] * 8
	plvalues[0] = pbcoilvalues[0]
	plvalues[1] = pbcoilvalues[1]
	plvalues[2] = pbcoilvalues[2]
	plvalues[3] = pbcoilvalues[3]


	# Pick and place.
	plvalues[4] = pbcoilvalues[4]
	plvalues[5] = pbcoilvalues[5]
	plvalues[6] = pbcoilvalues[6]
	"""
	plvalues = pbcoilvalues



	# Monitor the events and alarms.
	events = [False] * 8
	events[0] = (pumpflow != 0)
	events[1] = (pumpflow == 0)
	events[2] = (tank1level <= 5)
	events[3] = (tank1level >= 95)
	events[4] = (tank2level <= 5)
	events[5] = (tank2level >= 95)

	WriteServerData(15, 32300, 8, events)


	# Alarms.
	alarms = [False] * 8
	alarms[0] = pbcoilvalues[0]
	alarms[1] = pbcoilvalues[1]
	alarms[2] = pbcoilvalues[2]

	WriteServerData(15, 32400, 3, alarms)



	# Write the values to turn on the pilot lights.
	WriteServerData(15, 16, 8, plvalues)

	# Write out the multi-colour pilot light PL4.
	WriteServerData(16, 5001, 1, [PBFour])


	# Write the tank levels out to the server.
	WriteServerData(16, 5002, 2, [tank1level, tank2level])
	# Write out the pump speed display.
	WriteServerData(16, 5004, 2, [pumpflow, pumpflow])

	# Write out random numbers for the strip charts.
	WriteServerData(16, 5010, 2, [random.randint(-50, 50), random.randint(-50, 50)])

	# Now, wait a bit.
	time.sleep(0.2)

############################################################

