##############################################################################
# Project: 	MBLogic
# Module: 	GenClient.py
# Purpose: 	Generic Client Interface (server).
# Language:	Python 2.6
# Date:		23-May-2010.
# Version:	16-Mar-2011.
# Author:	M. Griffin.
# Copyright:	2010 - 2011 - Michael Griffin       <m.os.griffin@gmail.com>
#
# This file is part of MBLogic.
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
Implements the server part of a 'generic client' interface. The generic client
is intended to allow the creation of user client modules which can interface with
MBLogic without however having to be knit directly into the main system. 

The generic client system uses Twisted Perspective Broker, which is a standard 
part of the Twisted communications framework which MBLogic is based on.
"""

############################################################

import time
import subprocess
import os
import struct
import binascii

from twisted.spread import pb
from twisted.internet import task, reactor

import MBDataTable

############################################################

# Message texts.
_Msgs = {'configreq' : 'Generic client %s has requested configuration data.',
	'confignotfound' : 'Configuration data for generic client %s could not be found.',
	'clientstart' : 'Starting generic client %s',
	'clientnostart' : 'Could not start generic client %s',
	'clientnofind' : 'Could not find generic client %s',
	'forcestop' : 'Forcing terminate on generic client %s',
	'restarting' : 'Restarting generic client %s',
	'startlimit' : 'Restart limit on generic client %s exceeded',
	'diefinally' : 'Client %s terminated and will not be restarted',
}

############################################################
# This starts the generic clients.

class ClientLauncher:
	"""This automatically starts the generic clients.
	"""


	########################################################
	def __init__(self):
		"""
		"""
		# This is a copy of the client parameters.
		self._ClientParams = {}
		# This keeps track of the process.
		self._Clients = {}

		# This is the port used by the server.
		self._ServerPort = None
		# The maximum consecutive number of times to attempt to restart a client.
		self._StartLimit = 5
		# The number of check intervals to wait before deciding a client has 
		# really started or failed.
		self._RestartCheck = 5
		# This tracks whether the system is in the process of a shutdown.
		self._Terminating = False


	########################################################
	def _ClientMonitor(self):
		"""Check the current state of each client.
		"""
		for client, clientdata in self._Clients.items():

			# Find the current state of the client.
			clientstate = clientdata['clientid'].poll()


			# Skip this if it is not to be restarted.
			if clientdata['state'] != 'failed':

				# Restart limit is exceeded.
				if clientdata['startcount'] >= self._StartLimit:
					# Don't try any more.
					clientdata['state'] = 'failed'
					print(_Msgs['startlimit'] % client)

				# Client is running.
				elif (clientstate == None) and (clientdata['restartcheck'] >= self._RestartCheck):
					clientdata['startcount'] = 0

				# Client is still starting up.
				elif (clientstate == None) and (clientdata['restartcheck'] < self._RestartCheck):
					clientdata['restartcheck'] += 1

				# Client is not running and must be restarted.
				elif self._ClientParams[client]['restartonfail'] != 'no':
					# Increment the start attempt counter.
					clientdata['startcount'] += 1
					clientdata['restartcheck'] = 0
					# Restart the client.
					print(_Msgs['restarting'] % client)
					self.LaunchClient(client)

				# We should only get this if the client has failed, but is not to be restarted.
				else:
					# Don't try any more.
					clientdata['state'] = 'failed'
					print(_Msgs['diefinally'] % client)



	########################################################
	def ShutdownMonitor(self):
		"""This returns the number of processes still running. This is intended
		for monitoring whether clients have shut down.
		"""
		clientcount = 0
		for client, clientdata in self._Clients.items():

			# Find the current state of the client.
			try:
				clientstate = clientdata['clientid'].poll()
				# If the process is equal to None, it is still running.
				if clientstate != None:
					clientcount += 1
			except:
				pass

		return clientcount


	########################################################
	def SetClientParamList(self, clientparamlist, port):
		"""Set the generic client list parameters.
		Parameters: clientparamlist (dict) = The client parameters.
			port (integer) = The IP port number to tell the client 
				to contact after it starts up.
		"""
		# Get the client parameters.
		self._ClientParams = dict(map(lambda client: (client[0], client[1].GetConfigInfo()), clientparamlist.items()))
		self._ServerPort = port



	########################################################
	def LaunchClient(self, client):
		"""Start a generic client. Does not check to see if the client
		is already running.
		Parameters: client (string) = The name of the generic client.
		"""
		params = self._ClientParams[client]

		# The client is not already running, so try to start it.
		paramargs = params['clientfile'].split()
		cmdargs = ['python']
		filename = os.path.join('genclient', paramargs[0])
		cmdargs.append(filename)
		cmdargs.extend(paramargs[1:])
		cmdargs.extend(['-c', params['connectionname']])
		cmdargs.extend(['-p', self._ServerPort])

		# Make sure all the command arguments are strings.
		cmdargs = map(str, cmdargs)
		# Check if the file exists.
		if os.path.isfile(filename):
			try:
				self._Clients[client] = {'clientid' : subprocess.Popen(cmdargs), 
										'startcount' : 0, 
										'restartcheck' : 0,
										'state' : 'started'}
				print(_Msgs['clientstart'] % client)
			except:
				print(_Msgs['clientnostart'] % client)
		else:
			print(_Msgs['clientnofind'] % client)



	########################################################
	def LaunchAll(self):
		"""Start all the generic clients.
		"""
		for client in self._ClientParams.keys():
			# Don't start the client if it is marked as 'nostart'.
			if self._ClientParams[client]['restartonfail'] != 'nostart':
				self.LaunchClient(client)
				
		# This monitors the clients so they can be automatically restarted.
		self._ClientMon = task.LoopingCall(self._ClientMonitor)
		self._ClientMon.start(1.0)



	########################################################
	def NoRestart(self):
		"""Stop the automatic restart process. This prevents the system from
		automatically restarting halted clients.
		"""
		# Remove all the clients from the monitor so they won't get restarted.
		self._Clients = {}
		


	########################################################
	def TerminateAll(self):
		"""Terminate any generic clients which may be running. This is
		the final part of a system shutdown.
		"""
		# Flag that we are shutting down.
		self._Terminating = True

		# Shutdown clients.
		for client, clientid in self._Clients.items():
			try:
				if clientid.poll() == None:
					clientid.terminate()
					print(_Msgs['forcestop'] % client)
			except:
				# If it won't stop, there is nothing we can do
				# at this point as the system is shutting down
				# anyway.
				pass

		# Remove the clients from the monitor so they won't get restarted.
		self._Clients = {}




GenClientLanucher = ClientLauncher()


############################################################
# The following are remote exceptions raised when errors are detected.


class DataTableError(pb.Error):
	"""The specified parameter was invalid.
	"""
	pass

class ConfigErrors(pb.Error):
	"""An error occured while trying to retrieve the requested parameters.
	"""
	pass

class CmdError(pb.Error):
	"""An error occured while trying to retrieve the requested server command.
	"""
	pass


# The following are used for direct data table access operations.
class DTAccessAddrError(pb.Error):
	"""The address is out of range or of the wrong type.
	"""
	pass

class DTAccessQtyError(pb.Error):
	"""The quantity is out of range or of the wrong type.
	"""
	pass

class DTAccessParamError(pb.Error):
	"""A parameter is of the wrong type.
	"""
	pass

class DTAccessValueError(pb.Error):
	"""The value is missing, out of range, or of the wrong type.
	"""
	pass



############################################################

class GenClientServer(pb.Root):
	"""Handles generic client interface.
	"""


	########################################################
	def __init__(self):

		# Client parameters.
		self._ClientParams = {}
		# Client configurations.
		self._ClientConfig = {}


		# Client command states.
		self._ClientCmds = {}
		# Client status.
		self._ClientStatus = {}
		# Connection status reported from clients.
		self._ConnectStatus = {}
		# Command status reported from clients.
		self._CmdStatus = {}

		# Client watch dog timers.
		self._ClientWatchDogs = {}
		# Client watchdog time out (in seconds).
		self._WDTimeOut = 5.0

		# Client status information.
		self._StatusInfo = None

		# Call the connection monitor regularly to see if the connection 
		# is still active.
		self._ConnectionMon = task.LoopingCall(self._ConnectionMonitor)
		self._ConnectionMon.start(1.0)



	########################################################
	def SetStatusInfo(self, statusinfo):
		""" Must call this to add a reference to the configuration 
		information. This allows status information to be
		tracked and reported.
		"""
		self._StatusInfo = statusinfo


	########################################################
	def SetClientParams(self, clientparams):
		""" Must call this to provide the generic client parameters. Each 
		generic client will ask for this information when it starts up.
		Parameters: clientparams (list) = List of client parameter 
			container objects.
		"""
		self._ClientParams = {}
		self._ClientConfig = {}
		self._ClientCmds = {}
		for client in clientparams:
			clientname = client.GetConnectionName()
			self._ClientParams[clientname] = client
			self._ClientConfig[clientname] = client.GetConfigInfo()
			self._ClientCmds[clientname] = 'run'



	########################################################
	def StartAllClients(self):
		"""
		"""
		# Get the port number for the clients to use.
		port = self._StatusInfo.GetHostInfo()
		# Initialise the client launcher.
		GenClientLanucher.SetClientParamList(self._ClientParams, port)
		# Start the clients.
		GenClientLanucher.LaunchAll()


	########################################################
	def ClientStartWithDelay(self, delay):
		"""Start the clients after a specified delay.
		"""
		reactor.callLater(delay, self.StartAllClients)


	########################################################
	def _ConnectionMonitor(self):
		"""This is called regularly to monitor the connection count.
		"""
		timestamp = time.time()
		# Count the number of connections which have not exceeded the watchdog limit.
		wdcount = len(filter(lambda x: (timestamp - x[1]) < self._WDTimeOut, self._ClientWatchDogs.items()))
		if self._StatusInfo:
			self._StatusInfo.SetConnectionCount(wdcount)

		# Find out which (if any) clients have exceeded the watchdog count.
		wdtimeout = filter(lambda x: (timestamp - x[1]) > self._WDTimeOut, self._ClientWatchDogs.items())

		for clientname, elapsed in wdtimeout:
			self._ClientParams[clientname].SetConStatus('faulted')




	########################################################
	def SetCmdStopAll(self):
		"""Set the status to 'stop' for all the clients.
		"""
		# Tell the autoamtic restart process to stop checking any
		# of the clients. This allows the clients to stop themselves
		# in a controlled manner without being restarted.
		GenClientLanucher.NoRestart()

		# Send a controlled stop signal to each client.
		for i in self._ClientCmds:
			self._ClientCmds[i] = 'stop'



	########################################################
	def remote_GetParams(self, clientname):
	    	"""Returns the configuration parameters in a dictionary.
	    	"""
		try:
			print(_Msgs['configreq'] % clientname)
			return self._ClientConfig[clientname]
		except:
			print(_Msgs['confignotfound'] % clientname)
			raise ConfigErrors



	########################################################
	def _EncodeDataTable(self, dtable):
		"""Encode the data table lists to hex strings. This is used to improve
		performance when transfering the data via Perspective Broker.
		Parameters: dtable (dict) = A dictionary containing the data table.
		Returns (dict) = A dictionary containing the resulting encoded data. 
		"""
		encodedtable = {}
		# Coils.
		try:
			encodedtable['coil'] = binascii.hexlify(struct.pack('>%db' % len(dtable['coil']), *dtable['coil']))
		except:
			pass

		# Discrete inputs.
		try:
			encodedtable['inp'] = binascii.hexlify(struct.pack('>%db' % len(dtable['inp']), *dtable['inp']))
		except:
			pass

		# Holding registers.
		try:
			encodedtable['holdingreg'] = binascii.hexlify(struct.pack('>%dh' % len(dtable['holdingreg']), *dtable['holdingreg']))
		except:
			pass

		# Input registers.
		try:
			encodedtable['inpreg'] = binascii.hexlify(struct.pack('>%dh' % len(dtable['inpreg']), *dtable['inpreg']))
		except:
			pass

		return encodedtable


	########################################################
	def _DecodeDataTable(self, dtable):
		"""Decode hex strings into data table lists. This is used to improve
		performance when transfering the data via Perspective Broker.
		Parameters: dtable (dict) = A dictionary containing the encoded data.
		Returns (dict) = A dictionary containing the resulting decoded data. 
		"""
		# TODO: Debian 5.0 compatibility. Newer versions of struct can convert directly to bool.
		decodedtable = {}
		# Coils.
		try:
			msgdata = binascii.unhexlify(dtable['coil'])
			decodedtable['coil'] = map(bool, struct.unpack('>%db' % len(msgdata), msgdata))
		except:
			pass

		# Discrete inputs.
		try:
			msgdata = binascii.unhexlify(dtable['inp'])
			decodedtable['inp'] = map(bool, struct.unpack('>%db' % len(msgdata), msgdata))
		except:
			pass

		# Holding registers.
		try:
			msgdata = binascii.unhexlify(dtable['holdingreg'])
			decodedtable['holdingreg'] = list(struct.unpack('>%dh' % (len(msgdata) / 2), msgdata))
		except:
			pass

		# Input registers.
		try:
			msgdata = binascii.unhexlify(dtable['inpreg'])
			decodedtable['inpreg'] = list(struct.unpack('>%dh' % (len(msgdata) / 2), msgdata))
		except:
			pass

		return decodedtable



	########################################################
	def remote_GetServerCmd(self, clientname, status, connectstatus, cmdstatus, clientmsgs, writetable):
	    	"""Returns the current server command and informs the server
	    		of the current client status. We also count the number
	    		of clients in the 'running' state.
	    	Parameters: clientname (string) = The name of the client making
		    		the request.
			status (string) = The status of the client.
			connectstatus (string) = The overall connection status.
			cmdstatus = The command status.
			clientmsgs (list) = The current list of client messages.
			writetable (dict) = The write data table.
		Returns: (string) = The server command.
	    	"""
		# Handle the status and commands.
		try:
			# Client watchdog.
			self._ClientWatchDogs[clientname] = time.time()
			# Current client status.
			self._ClientStatus[clientname] = status

			# Current connection status.
			self._ClientParams[clientname].SetConStatus(connectstatus)
			# Current command status.
			self._ClientParams[clientname].AddCmdStatus(cmdstatus)


			# Current command status.
			self._CmdStatus[clientname] = cmdstatus

			# Update the client messages.
			self._ClientParams[clientname].SetClientMsgs(clientmsgs)


			# Decode the write data table.
			wrtable = self._DecodeDataTable(writetable)


			# If we have parameters for this client, start updating
			# the server data table.
			if clientname in self._ClientConfig:
				# Write the client data to the server data table.
				self._WriteDataTable(clientname, wrtable)
				# Read the server data table.
				readdt = self._ReadDataTable(clientname)
			else:
				readdt = {}

			# Encode the read data table.
			rdtable = self._EncodeDataTable(readdt)

			# Return any server commands to the client.
			return (self._ClientCmds[clientname], rdtable)
		except:
			raise CmdError


	########################################################
	def _ReadDataTable(self, clientname):
		"""Read the server data table and construct a dictionary
		to be forwarded to the client.
		"""
		readdict = {}
		# Get the parameters for this client.
		try:
			clientparams = self._ClientConfig[clientname]['readtable']
		except:
			return

		# Read the discrete inputs.
		try:
			addr, qty = clientparams['inp']
			readdict['inp'] = MBDataTable.MemMap.GetDiscreteInputsBoolList(addr, qty)
		except:
			pass

		# Read the coils.
		try:
			addr, qty = clientparams['coil']
			readdict['coil'] = MBDataTable.MemMap.GetCoilsBoolList(addr, qty)
		except:
			pass

		# Read the input registers.
		try:
			addr, qty = clientparams['inpreg']
			readdict['inpreg'] = MBDataTable.MemMap.GetInputRegistersIntList(addr, qty)
		except:
			pass

		# Read the holding registers.
		try:
			addr, qty = clientparams['holdingreg']
			readdict['holdingreg'] = MBDataTable.MemMap.GetHoldingRegistersIntList(addr, qty)
		except:
			pass

		return readdict

	########################################################
	def _WriteDataTable(self, clientname, writetable):
		"""Write the client values to the server data table.
		"""

		# Get the parameters for this client.
		try:
			clientparams = self._ClientConfig[clientname]['writetable']
		except:
			return

		# Read the discrete inputs.
		try:
			addr, qty = clientparams['inp']
			values = writetable['inp']
			# Limit the data written to no more than configured.
			if len(values) > qty:
				values = values[:qty]
			# Make sure the values are of the right type.
			checkedvals = map(bool, values)
			if len(checkedvals) > 0:
				MBDataTable.MemMap.SetDiscreteInputsBoolList(addr, len(checkedvals), checkedvals)
		except:
			pass

		# Read the coils.
		try:
			addr, qty = clientparams['coil']
			values = writetable['coil']
			if len(values) > qty:
				values = values[:qty]
			# Make sure the values are of the right type.
			checkedvals = map(bool, values)
			if len(checkedvals) > 0:
				MBDataTable.MemMap.SetCoilsBoolList(addr, len(checkedvals), checkedvals)
		except:
			pass

		# Read the input registers.
		try:
			addr, qty = clientparams['inpreg']
			values = writetable['inpreg']
			if len(values) > qty:
				values = values[:qty]
			# Make sure the values are of the right type.
			checkedvals = map(int, values)
			# Check the data range.
			if (max(checkedvals) <= 32767) and (min(checkedvals) >= -32768) and (len(checkedvals) > 0):
				MBDataTable.MemMap.SetInputRegistersIntList(addr, len(checkedvals), checkedvals)
		except:
			pass

		# Read the holding registers.
		try:
			addr, qty = clientparams['holdingreg']
			values = writetable['holdingreg']
			if len(values) > qty:
				values = values[:qty]
			# Make sure the values are of the right type.
			checkedvals = map(int, values)
			# Check the data range.
			if (max(checkedvals) <= 32767) and (min(checkedvals) >= -32768) and (len(checkedvals) > 0):
				MBDataTable.MemMap.SetHoldingRegistersIntList(addr, len(checkedvals), checkedvals)
		except:
			pass



	########################################################
	# The following are used for direct data table access.


	########################################################
	def remote_GetDiscreteInputs(self, addr, qty):
		"""Read the discrete inputs.
		addr (int) = The data table address to read.
		qty (int) = The number of addresses to read.
		"""
		try:
			# Check if the address is within range.
			if (addr > 65535) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 65535):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		return MBDataTable.MemMap.GetDiscreteInputsBoolList(addr, qty)


	########################################################
	def remote_GetCoils(self, addr, qty):
		"""Read the coils.
		addr (int) = The data table address to read.
		qty (int) = The number of addresses to read.
		"""
		try:
			# Check if the address is within range.
			if (addr > 65535) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 65535):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		return MBDataTable.MemMap.GetCoilsBoolList(addr, qty)


	########################################################
	def remote_GetInputRegisters(self, addr, qty):
		"""Read the input registers.
		addr (int) = The data table address to read.
		qty (int) = The number of addresses to read.
		"""
		try:
			# Check if the address is within range.
			if (addr > 65535) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 65535):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		return MBDataTable.MemMap.GetInputRegistersIntList(addr, qty)


	########################################################
	def remote_GetHoldingRegisters(self, addr, qty):
		"""Read the holding registers.
		addr (int) = The data table address to read.
		qty (int) = The number of addresses to read.
		"""
		try:
			# Check if the address is within range.
			if (addr > 1048575) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 1048575):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		return MBDataTable.MemMap.GetHoldingRegistersIntList(addr, qty)



	########################################################
	def remote_SetDiscreteInputs(self, addr, qty, values):
		"""Write the discrete inputs.
		addr (int) = The data table address to write.
		qty (int) = The number of addresses to write.
		values (list) = The list of values to write. This should be a
			list of booleans.
		"""
		try:
			# Check if the address is within range.
			if (addr > 65535) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 65535):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		# Limit the data written to no more than requested.
		if len(values) > qty:
			values = values[:qty]
		# Make sure the values are of the right type.
		checkedvals = map(bool, values)
		if len(checkedvals) <= 0:
			raise DTAccessValueError

		MBDataTable.MemMap.SetDiscreteInputsBoolList(addr, len(checkedvals), checkedvals)


	########################################################
	def remote_SetCoils(self, addr, qty, values):
		"""Write the coils.
		addr (int) = The data table address to write.
		qty (int) = The number of addresses to write.
		values (list) = The list of values to write. This should be a
			list of booleans.
		"""
		try:
			# Check if the address is within range.
			if (addr > 65535) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 65535):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		# Limit the data written to no more than requested.
		if len(values) > qty:
			values = values[:qty]
		# Make sure the values are of the right type.
		checkedvals = map(bool, values)
		if len(checkedvals) <= 0:
			raise DTAccessValueError

		MBDataTable.MemMap.SetCoilsBoolList(addr, len(checkedvals), checkedvals)


	########################################################
	def remote_SetInputRegisters(self, addr, qty, values):
		"""Write the input registers.
		addr (int) = The data table address to write.
		qty (int) = The number of addresses to write.
		values (list) = The list of values to write. This should be a
			list of signed integers.
		"""
		try:
			# Check if the address is within range.
			if (addr > 65535) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 65535):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		# Limit the data written to no more than requested.
		if len(values) > qty:
			values = values[:qty]
		# Make sure the values are of the right type.
		checkedvals = map(int, values)
		# Check the data range.
		if (max(checkedvals) > 32767) or (min(checkedvals) < -32768) or (len(checkedvals) <= 0):
			raise DTAccessValueError

		MBDataTable.MemMap.SetInputRegistersIntList(addr, len(checkedvals), checkedvals)


	########################################################
	def remote_SetHoldingRegisters(self, addr, qty, values):
		"""Write the holding registers.
		addr (int) = The data table address to write.
		qty (int) = The number of addresses to write.
		values (list) = The list of values to write. This should be a
			list of signed integers.
		"""
		try:
			# Check if the address is within range.
			if (addr > 1048575) or (addr < 0):
				raise DTAccessAddrError
			# Check if the quantity is within range.
			if (qty <= 0) or ((qty + addr) > 1048575):
				raise DTAccessQtyError
		except:
			raise DTAccessParamError

		# Limit the data written to no more than requested.
		if len(values) > qty:
			values = values[:qty]
		# Make sure the values are of the right type.
		checkedvals = map(int, values)
		# Check the data range.
		if (max(checkedvals) > 32767) or (min(checkedvals) < -32768) or (len(checkedvals) <= 0):
			raise DTAccessValueError

		MBDataTable.MemMap.SetHoldingRegistersIntList(addr, len(checkedvals), checkedvals)




############################################################

# Create a generic server instance.

GenericServer = GenClientServer()


############################################################

