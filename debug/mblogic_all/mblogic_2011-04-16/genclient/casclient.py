#!/usr/bin/python

"""
This file should contain the user routines used to help implement the protocol
specific generic client functions.
"""

import time
import urllib2
import signal

import GenClientLib

############################################################
class UserClient:
	"""
	"""

	########################################################
	def __init__(self):
		"""
		"""
		# Configuration is OK.
		self._ConfigOK = False
		# Connection status.
		self._ConnectStatus = 'starting'
		# Command status.
		self._CmdStatusBuff = []

		# List of strings containing error messages.
		self._ErrorMsgs = []

		# Host configuration. 
		self._HostConfig = {}
		# Client configuration.
		self._ClientConfig = {}
		# Command list.
		self._CommandList = []
		self._CurrentCmd = 0
		# Client messages.
		self._ClientMsgs = []

		# Client status.
		self._ClientStatus = 'init'

		self._MsgID = 0

		# Default register data.
		self._RegData = [0,0]


		# This formats the command status messages
		self._StatusMsgs = GenClientLib.StatCodes()


	########################################################
	def _AddCmdStatus(self, cmd, statcode):
		"""Add the status for a command.
		"""
		self._CmdStatusBuff.append(self._StatusMsgs.FormatStatusCode(cmd, statcode))
		
		

	########################################################
	def GetClientMsgs(self):
		"""Return the list of client messages.
		"""
		return self._ClientMsgs


	########################################################
	def GetStatus(self):
		"""Return the current status. This must include the following:
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
	def SetParams(self, hostconfig, clientconfig, cmdlist):
		"""This must accept the configuration parameters
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

		faulterrs = []
		# Validate the expected parameters.
		try:
			repeattime = int(clientconfig['repeattime'])  / 1000.0
		except:
			faulterrs.append('Invalid repeat time.')

		try:
			retrytime = int(clientconfig['retrytime'])  / 1000.0
		except:
			faulterrs.append('Invalid retry time.')

		try:
			cmdtime = int(clientconfig['cmdtime'])  / 1000.0
		except:
			faulterrs.append('Invalid command time.')

		# Parse the commands.
		commands = []
		for cmd in cmdlist:
			try:
				cmdline = cmd[1].split(',')
				cmdstrip = map(lambda x: x.strip(), cmdline)
				commands.append((cmd[0], cmdstrip))
			except:
				faulterrs.append('Bad command %s' % str(cmd))

		if len(faulterrs) == 0:
			self._RepeatTime = repeattime
			self._RetryTime = retrytime
			self._CommandTime = cmdtime
			self._CommandList = commands
			self._CommandIter = iter(self._CommandList)
			self._CmdStatus = dict(map(lambda cmd: (cmd[0], (0, 'noresult', 'No Result')), self._CommandList))
			self._ConfigOK = True

		# TODO: Remove.
		if len(faulterrs) == 0:
			self._ClientMsgs.append('The parameters were ok.')

		# Save the errors.
		self._ClientMsgs.extend(faulterrs)



	########################################################
	def NextCommand(self, readtable, servercmd):
		"""This should execute the next command, whatever it is. This
		is called regularly by GenClient.
		Parameters: readtable (dict) = A dictionary containing a mirror of the
			requested portion of the server data table. E.g.
			{'coil' : [True, False, True, True], 'inp' : [True, False, True, True],
			'inpreg' : [], 'holdingreg' : [1234, 5678]}

			servercmd (string) = A command from the server. This will 
				consist of one of the following:
				'run' = Run normally.
				'pause' = Pause operation.
				'restart' = A restart is requested. The restart 
					request will remain in effect until new
					parameters are loaded.

		Returns: dict, float = 
			- A dictionary in the same format as the "readtable" input parameter. This 
				will contain the data to be written to the server.
			- The time in seconds to wait before running this function again.

			Data table items in excess of those configured for transfer will be ignored.
		"""
		data = {}
		# First check if we've got a good parameter set.
		if self._ConfigOK:


			# Get the next command.
			try:
				cmdname, cmdvalue = self._CommandIter.next()
				nextpoll = self._CommandTime
			except StopIteration:
				self._CommandIter = iter(self._CommandList)
				cmdname, cmdvalue = self._CommandIter.next()
				nextpoll = self._RepeatTime

			# Hypothetically we should do something with the command.
			msgreq = ''.join(cmdvalue)

			# Read the data using GET. 
			req = urllib2.Request(url = 'http://localhost:8080/statdata/' + msgreq)
			f = urllib2.urlopen(req)

			# Read the response.
			response = f.read()

			# We will just measure the length of the data response.
			datalen = len(response)

			if cmdname == '&cmd1':
				self._RegData[0] = datalen
			else:
				self._RegData[1] = datalen
			# The holding registers will contain the length of the responses.
			data['holdingreg'] = self._RegData

			# We will just put arbitrary data in for the coils.
			data['coil'] = [True, False, True, False]

			# Set the connection status.
			self._ConnectStatus = 'running'
			# Set the command status.
			self._AddCmdStatus(cmdname, 'ok')


		else:
			# Set the connection status.
			self._ConnectStatus = 'stopped'

			nextpoll = 1.0

		return data, nextpoll


############################################################



############################################################
# Signal handler.
def SigHandler(signum, frame):
	print('\nOperator terminated generic client %s at %s' % (clientname, time.ctime()))
	gencontrol.StopClient()

def SigTermHandler(signum, frame):
	print('\Received terminate signal for generic client %s at %s' % (clientname, time.ctime()))
	gencontrol.StopClient()



# Initialise the signal handler.
signal.signal(signal.SIGINT, SigHandler)
signal.signal(signal.SIGTERM, SigTermHandler)


############################################################

# Get the command line parameter options.
CmdOpts = GenClientLib.GetOptions()
port, clientname, startdelay = CmdOpts.GetStartParams()


# Initialise the generic client handler.
gencontrol = GenClientLib.GenClientController(port, clientname, UserClient)


print('\n\nStarting generic client %s at %s' % (clientname, time.ctime()))

# Delay the specified number of seconds. This will allow the main
# program to start up before trying to contact it.
time.sleep(startdelay)


# Start the generic client.
gencontrol.StartClient()

print('\n\nGeneric client %s halted at %s' % (clientname, time.ctime()))


