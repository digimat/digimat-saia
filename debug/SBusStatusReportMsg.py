##############################################################################
# Project: 	HMIServer
# Module: 	SBusStatusReportMsg.py
# Purpose: 	Format status report messages.
# Language:	Python 2.5
# Date:		19-Dec-2009.
# Ver.:		25-Nov-2010.
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

"""Format report messages.
"""

import binascii
from mbprotocols import ModbusDataLib

############################################################

# These strings define how the data is displayed. 
_sbsclientreqreportstr = 'msgseq: %d  addr: %d  cmd: %d  addr: %d  qty: %d  msgdata: %s'
_sbsclientrespreportstr = 'telattr: %d  msgseq: %d  data: %s'


def BreakString(reportstr):
	"""This splits the string up into groups of 8 separated by 
	spaces to allow line breaks on the report web page.
	"""
	return ''.join(['%s ' % reportstr[i:i + 8] for i in xrange(0, len(reportstr), 8)])


def _BoolList2Str(reportreqdata):
	"""Convert a list of boolean values to a string of '0' and '1' characters.
	Parameters: reportreqdata (list of boolean) = The list of data to be converted.
	Returns: (string) = A string of '0' and '1' characters equivalent to the 
		input parameter.
	"""
	return ''.join(map(str, map(int, reportreqdata)))

########################################################
def SBusClientFieldRequest(msgsequence, stnaddr, cmdcode, dataaddr, datacount, msgdata):
	"""Construct the report for a SBus field message request.
	msgsequence (integer) = Message sequence.
	stnaddr (integer) = Station address.
	cmdcode (integer) = Command code.
	dataaddr (integer) = Starting data table address.
	datacount (integer) = Number of data elements.
	msgdata (string) = The raw binary string containing the message data.
	"""

	try:
		if cmdcode in [2, 3, 5, 6]:
			reportreqdata = ''
		elif cmdcode in [11, 13]:	
			reportreqdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		elif cmdcode == 14:
			reportreqdata = binascii.hexlify(msgdata)
		else:
			reportreqdata = 'No data.'

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportreqdata)

		return _sbsclientreqreportstr % (msgsequence, stnaddr, cmdcode, dataaddr, datacount, reportstr)

	# If there was an error, we just ignore it and log some default data.
	except:
		return _sbsclientreqreportstr % (0, 0, 0, 0, 0, 'Request data error.')


########################################################
def SBusClientFieldResponse(cmdcode, telegramattr, msgsequence, msgdata):
	"""Construct the report for a SBus field message response.
	cmdcode (integer) = Command code.
	telegramattr (integer) = Telegram attribute.
	msgsequence (integer) = Message sequence.
	msgdata (string) = The response data as a binary string.
	"""

	try:
		if cmdcode in [2, 3, 5, 11, 13]:
			reportreqdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		elif cmdcode in [6, 14]:
			reportreqdata = binascii.hexlify(msgdata)
		else:
			reportreqdata = 'No data.'

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportreqdata)

		return _sbsclientrespreportstr % (telegramattr, msgsequence, reportstr)


	# If there was an error, we just ignore it and log some default data.
	except:
		return _sbsclientrespreportstr % (0, 0, 0, 'Response data error.')

##############################################################################


_sbsserverreqreportstr = 'telattr: %d  msgseq: %d  stnaddr: %d  cmd: %d  addr: %d  count: %d  data: %s'
_sbsserverrespreportstr = 'msgseq: %d  cmd: %d  acknak: %d  msgdata: %s'


########################################################
def SBusServerFieldRequest(telegramattr, msgsequence, stnaddr, cmdcode, dataaddr, datacount, msgdata):
	"""Construct the report for a SBus field message request.
	telegramattr (integer) = Telegram attribute.
	msgsequence (integer) = Message sequence.
	stnaddr (integer) = Station address.
	cmdcode (integer) = Command code.
	dataaddr (integer) = Starting data table address.
	datacount (integer) = Number of data elements.
	msgdata (string) = The raw binary string containing the message data.
	"""

	try:
		if cmdcode in [2, 3, 5, 11, 13]:
			reportreqdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		elif cmdcode in [6, 14]:
			reportreqdata = binascii.hexlify(msgdata)
		else:
			reportreqdata = 'No data.'

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportreqdata)

		return _sbsserverreqreportstr % (telegramattr, msgsequence, stnaddr, cmdcode, dataaddr, datacount, reportstr)

	# If there was an error, we just ignore it and log some default data.
	except:
		return _sbsserverreqreportstr % (0, 0, 0, 0, 0, 0, 'Request data error.')


########################################################
def SBusServerFieldResponse(msgsequence, cmdcode, msgdata, acknak):
	"""Construct the report for a SBus field message response.
	msgsequence (integer) = Message sequence.
	cmdcode (integer) = Command code.
	msgdata (string) = The response data as a binary string.
	acknak (integer) = Ack/Nak code.
	"""

	try:
		if cmdcode in [2, 3, 5, 11, 13]:
			reportreqdata = _BoolList2Str(ModbusDataLib.bin2boollist(msgdata))
		elif cmdcode in [6, 14]:
			reportreqdata = binascii.hexlify(msgdata)
		else:
			reportreqdata = 'No data.'

		# This splits the string up into groups separated by 
		# spaces to allow line breaks on the report web page.
		reportstr = BreakString(reportreqdata)
		return _sbsserverrespreportstr % (msgsequence, cmdcode, acknak, reportstr)


	# If there was an error, we just ignore it and log some default data.
	except:
		return _sbsserverrespreportstr % (0, 0, 0, 'Response data error.')

##############################################################################



