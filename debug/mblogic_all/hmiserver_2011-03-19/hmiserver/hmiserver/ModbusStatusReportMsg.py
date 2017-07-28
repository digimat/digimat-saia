##############################################################################
# Project: 	HMIServer
# Module: 	StatusReportMsg.py
# Purpose: 	Format status report messages for Modbus.
# Language:	Python 2.5
# Date:		28-Feb-2009.
# Ver.:		03-Dec-2010.
# Copyright:	2009 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

"""Format report messages for Modbus Clients and Servers.
"""

import binascii
from mbprotocols import ModbusDataLib

############################################################

_reqreportstr = 'tid: %d  uid: %d  func: %d  addr: %d  qty: %d  data: %s'
_respreportstr = 'tid: %d func: %d  data: %s'

def BreakString(reportstr):
	"""This splits the string up into groups of 4 separated by 
	spaces to allow line breaks on the report web page.
	"""
	return ''.join(['%s ' % reportstr[i:i + 4] for i in xrange(0, len(reportstr), 4)])


def _BoolList2Str(reportreqdata):
	"""Convert a list of boolean values to a string of '0' and '1' characters.
	Parameters: reportreqdata (list of boolean) = The list of data to be converted.
	Returns: (string) = A string of '0' and '1' characters equivalent to the 
		input parameter.
	"""
	return ''.join(map(str, map(int, reportreqdata)))

########################################################
def ModbusClientFieldRequest(transid, uid, functioncode, start, qty, msgdata):
	"""Construct the report for a Modbus/TCP field message request.
	transid (integer) = The transaction id. 
	uid (integer) = The unit id. 
	functioncode (integer) = The function code.
	start (integer) = The starting data table address.
	qty (integer) = The number of items requested.
	msgdata (string) = The raw binary string containing the message data.
	"""
	try:
		if functioncode in [1, 2, 3, 4]:
			reportreqdata = ''
		elif functioncode in [5, 6, 16]:
			reportreqdata = binascii.hexlify(msgdata)
		elif (functioncode == 15):
			reportreqdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		else:
			reportreqdata = 'No data.'

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportreqdata)

		return _reqreportstr % (transid, uid, functioncode, start, qty, reportstr)

	# If there was an error, we just ignore it and log some default data.
	except:
		return _reqreportstr % (0, 0, 0, 0, 0, 'Request data error.')


########################################################
def ModbusClientFieldResponse(transid, functioncode, msgdata):
	"""Construct the report for a Modbus/TCP field message request.
	transid (integer) = The transaction id. 
	functioncode (integer) = The function code.
	msgdata (string) = The response data as a binary string.
	"""

	try:
		if functioncode in [1, 2]:
			reportrespdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		elif functioncode in [3, 4, 5, 6, 15, 16]:
			reportrespdata = binascii.hexlify(msgdata)
		elif functioncode > 127:
			reportrespdata = binascii.hexlify(msgdata)
		else:
			reportrespdata = 'No data.'

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportrespdata)

		return _respreportstr % (transid, functioncode, reportstr)

	# If there was an error, we just ignore it and log some default data.
	except:
		return _respreportstr % (0, 0, 'Response data error.')


##############################################################################

########################################################
def ModbusServerFieldRequest(transid, unitid, functioncode, start, qty, msgdata):
	"""Construct the report for a Modbus/TCP field message request.
	transid (integer) = The transaction id. 
	unitid (integer) = The unit id.
	functioncode (integer) = The function code.
	start (integer) = The starting data table address.
	qty (integer) = The quantity of data.
	msgdata (string) = The raw binary string containing the message data.
	"""
	try:
		if functioncode in [1, 2, 3, 4]:
			reportreqdata = ''
		elif functioncode in [5, 6]:
			reportreqdata = binascii.hexlify(msgdata)
		elif (functioncode == 15):
			reportreqdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		elif (functioncode == 16):
			reportreqdata = binascii.hexlify(msgdata)
		else:
			reportreqdata = 'No data.'
			qty = 0

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportreqdata)

		return _reqreportstr % (transid, unitid, functioncode, start, qty, reportstr)

	# If there was an error, we just ignore it and log some default data.
	except:
		return _reqreportstr % (0, 0, 0, 0, 0, 'Request data error.')



########################################################
def ModbusServerFieldResponse(transid, functioncode, msgdata, requestdata, qty, exceptioncode):
	"""Construct the report for a Modbus/TCP field message request.
	transid (integer) = The transaction id. 
	functioncode (integer) = The function code.
	msgdata (string) = The response data as a binary string.
	requestdata (string) = The original request data.
	qty (integer) = The quantity of data.
	exceptioncode (integer) = The Modbus exception code (if error).
	"""

	try:
		if functioncode in [1, 2]:
			reportrespdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		elif functioncode in [3, 4]:
			reportrespdata = binascii.hexlify(msgdata)
		elif functioncode in [5, 6]:
			reportrespdata = '1'
		elif functioncode in [15, 16]:
			reportrespdata = str(qty)
		elif functioncode > 127:
			reportrespdata = str(exceptioncode)
		else:
			reportrespdata = 'No data.'

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportrespdata)

		return _respreportstr % (transid, functioncode, reportstr)

	# If there was an error, we just ignore it and log some default data.
	except:
		return _respreportstr % (0, 0, 'Response data error.')



##############################################################################

