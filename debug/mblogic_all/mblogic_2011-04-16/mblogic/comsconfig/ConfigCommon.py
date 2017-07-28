##############################################################################
# Project: 	MBLogic
# Module: 	ConfigCommon.py
# Purpose: 	Common configuration routines..
# Language:	Python 2.5
# Date:		22-Mar-2008.
# Version:	14-Oct-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
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

from mbprotocols import MBAddrTypes

"""Common configuration routines.
"""

########################################################

# Generic error messages.
ErrMsg = {
	'missingitem' : 'Comms config error in %(section)s - missing %(item)s',
	'unknownitem' : 'Comms config error in %(section)s - unknown %(item)s',
	'badservername' : 'Comms config error - invalid server name: %(section)s',
	'badport' : 'Comms config error - bad port number in %(section)s - %(paramvalue)s',

	'badclientname' : 'Comms config error - invalid client name: %(section)s',
	'badvalue' : 'Comms config error in %(section)s - %(item)s has a bad parameter value %(paramvalue)s',
	'badcmdname' : 'Comms config error in %(section)s - bad command name %(item)s',

	'badcmdfmt' : 'Comms config error in %(section)s - bad command format %(item)s  %(paramvalue)s',
	'missingcmdparam' : 'Comms config error in %(section)s - missing command parameter name %(item)s  %(paramvalue)s',
	'uknowncmdparam' : 'Comms config error in %(section)s - unkown command parameter name %(item)s  %(paramvalue)s',
	'badcmdparamval' : 'Comms config error in %(section)s - bad command parameter value %(item)s  %(paramvalue)s',


	# Modbus specific error messages.
	'badfunccode' : 'Comms config error in %(section)s - bad modbus function code %(item)s  %(paramvalue)s',
	'badqty' : 'Comms config error in %(section)s - bad modbus quantity %(item)s  %(paramvalue)s',
	'badmemaddr' : 'Comms config error in %(section)s - modbus memory address out of range %(item)s  %(paramvalue)s',
	'badremoteaddr' : 'Comms config error in %(section)s - modbus remote address out of range %(item)s  %(paramvalue)s',
	'baduid' : 'Comms config error in %(section)s - bad modbus unit id %(item)s  %(paramvalue)s',

	# General configuration messages.
	'noserverid' : 'Comms config error - No server id.',
	'badexpdt' : 'Comms config error - Bad expanded register map parameter.',
	'badfile' : 'Comms config error - No config file found. %(section)s',
	'badfileopen' : 'Comms edit error - Error opening file %(paramvalue)s for write',
	'badfilesave' : 'Comms edit error - Error saving file %(paramvalue)s',
	'badtype' : 'Comms config error - Unknown config type  %(item)s in %(section)s.',
	'badprotocol' : 'Comms config error - Unknown protocol type %(item)s in %(section)s.',
	'badsystem' : 'Comms config error - Cannot read parameters in %(section)s.'

	}


########################################################
def FormatErr(errkey, section, item, paramvalue):
	"""Format and return an error message. 
	Parameters:
		errkey (string) = A key to the error message dictionary.
		section (string) = The section name the error occured in.
		item (string) = The item the error occured in.
		paramvalue (string) = The parameter value which is in error.
	Returns (string) = The formatted error message.
	"""
	return (ErrMsg[errkey] % {'section' : section, 
					'item' : item, 'paramvalue' : paramvalue})



########################################################
def CheckHost(host):
	""" Validate a host name.
	Params: host (string) - Host hame. Checks for minimum length.
	Returns: (result, host)
		result (boolean). True if length of host is greater than zero
		host (string). Original parameter.
	"""
	# Host address.
	if (len(host) < 1):
		return False, host
	else:
		return True, host

########################################################
def CheckPort(port):
	""" Validate a port number, and convert the port to an integer.
	Params: port (string) - Port. Converts to integer.
	Returns: (result, port)
		result (boolean) = True if port was OK.
		port (integer) = Port number if OK, else it is the
				original port parameter passed in.
	"""
	# Port number must be integer.
	try:
		CheckedPort = int(port)
	except:
		return False, port

	# Ports must be positive numbers.
	if (CheckedPort < 0):
		return False, port

	# All tests passed.
	return True, CheckedPort


########################################################
def CheckTime(timevalue):
	""" Validate a time value in milliseconds.
	Params: timevalue (string) - Time in milliseconds.
	Returns: (result, time) 
		result (boolean) = True if time was OK.
		time (int) = The time in milli-seconds, or the original parameter 
			if there was an error.
	"""

	# Time delays between consecutive commands (specified in msec).
	try:
		TimeVal = int(timevalue)
	except:
		return False, timevalue

	# Must be +ve integer.
	if (TimeVal <= 0):
		return False, timevalue
	else:
		return True, TimeVal

########################################################
def CheckDTAddr(dtaddr, dttype):
	""" Validate a data table address.
	Params: dtaddr (string) - The data table address.
		dttype (string) - The data table address type (e.g. 'coil').
	Returns: (result, faultaddr)
		result (boolean) = True if time was OK.
		dtaddr (integer). Data table address. Original parameter if error.
	"""
	# Fault address number.
	try:
		DTAddr = int(dtaddr)	# Must be +ve integer.
	except:
		return False, dtaddr

	if ((DTAddr < 0) or (DTAddr > MBAddrTypes.MaxBasicAddrTypes[dttype])):
		return False, dtaddr

	# All tests passed.
	return True, DTAddr


# The following routines check the data table addresses for individual types.
#####
def CheckDTCoilAddr(dtaddr):
	"""Check data table coil addresses.
	"""
	return CheckDTAddr(dtaddr, 'coil')

#####
def CheckDTDisInpAddr(dtaddr):
	"""Check data table discrete input addresses.
	"""
	return CheckDTAddr(dtaddr, 'discrete')

#####
def CheckDTHRegAddr(dtaddr):
	"""Check data table holding register addresses.
	"""
	return CheckDTAddr(dtaddr, 'holdingreg')

#####
def CheckDTInpRegAddr(dtaddr):
	"""Check data table input register addresses.
	"""
	return CheckDTAddr(dtaddr, 'inputreg')


########################################################
def CheckGenRestart(restart):
	""" Validate a generic client restart parameter.
	Params: restart (string) - The permitted restart actions.
	Returns: (result, restart)
		result (boolean) = True if time was OK.
		restart (string). The original parameter.
	"""
	return (restart in ['yes', 'no', 'nostart']), restart



########################################################
def CheckGenDTAddr(dtaddr):
	""" Validate a generic data table address parameter set for reading or 
	or writing the data table. 
	Params: 
	dtaddr (string) - The data table address list. This will be in the
		format coil=9000:10, inp=9000:15, inpreg=9500:5, holdingreg=9600:4
		Each address type is optional, so there may be any number of these
		from 1 to 4. As a special case, 'none' indicates the parameter
		is not used.
	Returns: (result, addrconfig)
		result (boolean) = True if time was OK.
		addrconfig (dictionary). Data table address configuration. 
			Original parameter if error.
	"""

	# If the parameter is 'none', this is a special case to indicate 
	# the parameter is unused and there are no addresses expected.
	if dtaddr.strip() == 'none':
		return True, {}

	try:
		# First, split the parameter string by commas.
		paramlist = dtaddr.split(',')
		# Split each into parameter name and parameters (by '=').
		paramlist = map(lambda param: param.split('=', 1), paramlist)
		# Split the address and length (by ':') and trim blanks from the parameter name.
		paramlist = map(lambda param: (param[0].strip(), param[1].split(':', 1)), paramlist)
		# Look for unrecognised parameter names.
		badnames = filter(lambda param: param[0] not in ('coil', 'inp', 'inpreg', 'holdingreg'), paramlist)
		# Convert the parameter values into integers.
		paramlist = map(lambda param: (param[0], (int(param[1][0]), int(param[1][1]))), paramlist)
		# Check the address ranges for negative numbers.
		negatives = filter(lambda param: param[1][0] < 0 or param[1][1] < 0, paramlist)
		# Check for address that are too large.
		outofrange = filter(lambda param: param[0] == 'coil' and 
			(param[1][0] + param[1][1]) > MBAddrTypes.MaxBasicAddrTypes['coil'], paramlist)
		outofrange.extend(filter(lambda param: param[0] == 'inp' and 
			(param[1][0] + param[1][1]) > MBAddrTypes.MaxBasicAddrTypes['discrete'], paramlist))
		outofrange.extend(filter(lambda param: param[0] == 'inpreg' and 
			(param[1][0] + param[1][1]) > MBAddrTypes.MaxBasicAddrTypes['inputreg'], paramlist))
		outofrange.extend(filter(lambda param: param[0] == 'holdingreg' and 
			(param[1][0] + param[1][1]) > MBAddrTypes.MaxBasicAddrTypes['holdingreg'], paramlist))
	except:
		return False, dtaddr


	if (len(badnames) > 0) or (len(negatives) > 0) or (len(outofrange) > 0):
		return False, dtaddr

	return True, dict(paramlist)



########################################################
def ValidateSectionName(sectionname):
	"""Validate that the section name is properly formed.
	Parameters: sectionname (string) = The section name to check.
	Returns (result, sectionname)
		result (boolean) = True if time was OK.
		sectionname (string) = Original parameter.
	"""
	# Client names must be at least 1 character long.
	if (len(sectionname) < 1):
		return False, sectionname

	# Client names must not begin with a '&'
	if (sectionname[0:1] == '&'):
		return False, sectionname

	return True, sectionname


########################################################
def IsCmdName(commandname):
	"""Returns true if the item name matches the format for
	a command name. 
	Parameters: commandname (string) = Item name to check.
	Returns: (boolean) = True if command name.
	""" 
	return ((commandname[0:1] != '&') and (len(commandname) < 2))


########################################################
def CheckAny(param):
	"""Always returns True. We use this for any parameters that we want
	to ignore for now.
	"""
	return True, param



########################################################
def CheckSerialPort(portname):
	"""Returns true if the item name matches the format for
	a serial port. 
	Parameters: portname = port name or number to check.
	Returns: (boolean) = True if port name is a valid format.
	""" 
	return True, portname



########################################################
def CheckBaudRate(baudrate):
	""" Validate a baud rate number, and convert it to an integer.
	This only checks that the rate is a valid positive integer.
	Params: baudrate (string) - Baud rate. Converts to integer.
	Returns: (result, baudrate)
		result (boolean) = True if port was OK.
		baudrate (integer) = Baudrate number if OK, else it is the
				original parameter passed in.
	"""
	# Baud rate number must be integer.
	try:
		CheckedBaud = int(baudrate)
	except:
		return False, baudrate

	# Baudrates must be positive numbers.
	if (CheckedBaud < 0):
		return False, baudrate

	# All tests passed.
	return True, CheckedBaud



########################################################
def CheckParity(parity):
	"""Returns true if the item name matches the format for
	parity. 
	Parameters: parity (string) = parity to check.
	Returns: (boolean) = True if parity name is correct.
		Parity (string) = The original parameter.
	""" 
	return parity in ('none', 'odd', 'even', 'mark', 'space'), parity


########################################################
def CheckDataBits(databits):
	"""Returns true if the item name matches the format for
	data bits. 
	Parameters: databits (string) = Value to check.
	Returns: (boolean) = True if ok.
		datatbits (integer) = Databits number if OK, else it is the
				original parameter passed in.
	""" 
	# Number must be integer.
	try:
		CheckedDB = int(databits)
	except:
		return False, databits

	# Must be in the following range.
	if (CheckedDB < 5) or (CheckedDB > 8):
		return False, databits

	# All tests passed.
	return True, CheckedDB


########################################################
def CheckStopBits(stopbits):
	"""Returns true if the item name matches the format for
	stop bits. 
	Parameters: stopbits (string) = stopbits to check.
	Returns: (boolean) = True if name is correct.
		stopbits (string) = The original parameter.
	""" 
	return stopbits in ('1', '1.5', '2'), stopbits


########################################################






