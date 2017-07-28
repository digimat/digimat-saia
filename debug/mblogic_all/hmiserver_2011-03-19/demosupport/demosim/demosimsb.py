#!/usr/bin/python
##############################################################################
# Project: 	HMIServer
# Module: 	demosimsb.py
# Purpose: 	Simulate a tank process for the HMI demo.
# Language:	Python 2.5
# Date:		26-Feb-2009.
# Ver:		16-Mar-2011.
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
This version is for SBus Ethernet.
"""

############################################################

import sys
import signal
import time
import random

from mbprotocols import SBusSimpleClient
from mbprotocols import SBusMsg
from mbprotocols import ModbusDataLib

############################################################

print('\nStarting the SBus demosim 2.1 at %s' % time.ctime())

# Signal handler.
def SigHandler(signum, frame):
	print('Operator terminated demosimsb at %s\n' % time.ctime())
	sys.exit()


# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)

############################################################

servport = 5050

# If the server is not ready, we back off and try again later.
contactcount = 10
servercontacted = False
while not servercontacted:
	try:
		client = SBusSimpleClient.SBusSimpleClient('localhost', servport, 5.0)
		servercontacted = True
	except:
		if (contactcount > 0):
			print('demosim could not contact the server at port %s. Will retry in 30 seconds...' % servport)
			contactcount -= 1
			time.sleep(30)
		else:
			print('demosim could not contact the server at port %s. Exiting...' % servport)
			sys.exit()



def ContactServer():
	client.SendRequest(1, 1, 2, 1, 0)
	# Get the reply.
	TeleAttr, MsgSeq, MsgData = client.ReceiveResponse()
	
# Now, check to see if we can actually talk to the server.
responseok = False
contactcount = 10
while not responseok:
	try:
		ContactServer()
		responseok = True
	except:
		if (contactcount > 0):
			print('Demosim - could not poll the server at port %s. Will retry in 30 seconds...' % servport)
			contactcount -= 1
			time.sleep(30)
		else:
			print('Demosim - could not poll the server at port %s. Exiting...' % servport)
			sys.exit()
		



############################################################

# Counter to increment the message sequence.
class MsgSequence:
	def __init__(self):
		self._msgseq = 0
	def incseq(self):
		self._msgseq += 1
	def getseq(self):
		return self._msgseq

MsgSeqCounter = MsgSequence()


def GetServerData(cmd, adr, qty):
	MsgSeqCounter.incseq()
	# Send the request.
	client.SendRequest(MsgSeqCounter.getseq(), 1, cmd, qty, adr)
	# Get the reply.
	TeleAttr, MsgSeq, MsgData = client.ReceiveResponse()
	# Decode the data.
	if (cmd in (2, 3, 5)):
		try:
			values = ModbusDataLib.bin2boollist(MsgData)
		except:
			return []
	elif (cmd == 6):
		try:
			values = SBusMsg.signedbin2int32list(MsgData)
		except:
			return []
	else:
		print('Bad command code %s when reading data.' % cmd)
		return []
	return values

def WriteServerData(cmd, adr, qty, data):
	if (cmd == 11):
		msgdata = ModbusDataLib.boollist2bin(data)
	elif (cmd == 14):
		msgdata = SBusMsg.signedint32list2bin(data)
	else:
		print('Bad command code %s when writing data.' % cmd)
		return

	MsgSeqCounter.incseq()
	# Send the request.
	client.SendRequest(MsgSeqCounter.getseq(), 1, cmd, qty, adr, msgdata)
	# Get the reply.
	TeleAttr, MsgSeq, MsgData = client.ReceiveResponse()

############################################################

PBFour = 0
pumpflow = 0
tank1level = 0
tank2level = 0

LoopCount = 0

# Loop forever.
while True:
	# Read the push button coils.
	pbcoilvalues = GetServerData(2, 0, 8)
	# Read the push button, tank, and pump holding registers.
	regreadvalues = GetServerData(6, 5000, 8)


	if len(regreadvalues) >= 5:
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
	plvalues = pbcoilvalues



	# Monitor the events and alarms.
	events = [False] * 8
	events[0] = (pumpflow != 0)
	events[1] = (pumpflow == 0)
	events[2] = (tank1level <= 5)
	events[3] = (tank1level >= 95)
	events[4] = (tank2level <= 5)
	events[5] = (tank2level >= 95)

	WriteServerData(11, 32300, 8, events)


	# Alarms.
	alarms = [False] * 8
	alarms[0] = pbcoilvalues[0]
	alarms[1] = pbcoilvalues[1]
	alarms[2] = pbcoilvalues[2]

	WriteServerData(11, 32400, 3, alarms)



	# Write the values to turn on the pilot lights.
	try:
		WriteServerData(11, 16, 8, plvalues)
	except:
		pass

	# Write out the multi-colour pilot light PL4.
	try:
		WriteServerData(14, 5001, 1, [PBFour])
	except:
		pass


	# Write the tank levels out to the server.
	try:
		WriteServerData(14, 5002, 2, [tank1level, tank2level])
	except:
		pass

	# Write out the pump speed display.
	try:
		WriteServerData(14, 5004, 2, [pumpflow, pumpflow])
	except:
		pass

	# Write out random numbers for the strip charts.
	try:
		WriteServerData(14, 5010, 2, [random.randint(-50, 50), random.randint(-50, 50)])
	except:
		pass

	# Now, wait a bit.
	time.sleep(0.2)

############################################################

