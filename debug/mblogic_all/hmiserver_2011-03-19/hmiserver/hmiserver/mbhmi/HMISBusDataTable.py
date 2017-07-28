##############################################################################
# Project: 	MBLogic
# Module: 	HMISBusDataTable.py
# Purpose: 	Pass HMI requests on to a Modbus type data table.
# Language:	Python 2.5
# Date:		09-May-2009.
# Ver.:		04-May-2010.
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

"""This module converts HMI read and write requests into an SBus type data table. 
"""

############################################################

from mbprotocols import SBusExtData

############################################################


############################################################

class HMIDataTable:
	"""Provide methods for reading and writing an SBus type data table. These
	are used by higher HMI data handling routines to process HMI messages.
	"""


	########################################################
	def __init__(self, datatable):
		"""datatable (object) = An object which provides methods for
		reading and writing the data table. The ones expected are:
		1) GetFlagsBool = Read a single flag.
		2) GetInputsBool = Read a single input.
		3) GetOutputsBool = Read a single output.
		4) GetRegistersInt = Read a single register.
		5) SetFlagsBool = Write to a single flag.
		6) SetRegistersInt = Write to a single register.

		Routines to access extended data types are handled through a
		separate object, which is given a reference to the same data table.
		"""
		self._DataTable = datatable
		# This handles extended data types. These are data types which 
		# span several adjacent registers.
		self._ExtData = SBusExtData.ExtendedDataTypes(self._DataTable)


	########################################################
	def GetEventStates(self, eventlist):
		"""Get the current states of a list of events.
		Params: eventlist (list) - a list of SBus flag addresses.
			E.g. [23, 100, 52]
		Returns: (dict) - A dictionary where SBus flag addresses are
			keys, and the states are boolean values.
			E.g. {23 : 0, 100 : 1, 52 : 1}
		"""
		result = {}
		for i in eventlist:
			result[i] = self._DataTable.GetFlagsBool(i)
		return result

	########################################################
	def GetAlarmStates(self, alarmlist):
		"""Get the current states of a list of alarms.
		Params: eventlist (list) - a list of SBus flag addresses.
			E.g. [23, 100, 52]
		Returns: (dict) - A dictionary where SBus flags addresses are
			keys, and the states are boolean values.
			E.g. {23 : 0, 100 : 1, 52 : 1}
		"""
		result = {}
		for i in alarmlist:
			result[i] = self._DataTable.GetFlagsBool(i)
		return result


	########################################################
	def AddressWritable(self, addrtype):
		"""This is used to test if the address type is writable.
		Returns 'writeable' if the address type is writable. 
		Returns 'writeprotected' if the address type is not writable.
		Returns 'unknown' if the address type is unknown.
		"""
		if addrtype in ['sbusflag', 'sbusoutput', 'sbusreg', 'sbusregstr']:
			return 'writeable'
		elif addrtype == 'sbusinput':
			return 'writeprotected'
		else:
			return 'unknown'


	########################################################
	def GetDataValues(self, addrlist):
		"""Get the current values from the data source.
		Params: addrlist (list) = A list of tuples containing tag name, 
			SBus address types, data types, and memory addresses. 
			E.g. [('PB1', 'sbusflag', 'boolean', 5000), 
				('PB2', 'sbusflag', 'boolean', 4998), 
				('PumpSpeed', 'sbusreg', 'integer', 23)]
		Returns: (dict), (dict) = Two dictionary where the keys are the 
			tag names. The first dictionary contains any successful read
			results. The second contains error codes.
			E.g. {'PB1' : 1, 'PumpSpeed' : 1825}, {'PB2' : 'addresserror'}
		"""
		regresult = {}		# Register data.
		dataerrors = {}		# Errors.

		for tagname, addrtype, datatype, memaddr in addrlist:
			try:
				if (addrtype == 'sbusflag'):
					regresult[tagname] = int(self._DataTable.GetFlagsBool(memaddr))

				elif (addrtype == 'sbusinput'):
					regresult[tagname] = int(self._DataTable.GetInputsBool(memaddr))

				elif (addrtype == 'sbusoutput'):
					regresult[tagname] = int(self._DataTable.GetOutputsBool(memaddr))

				elif (addrtype == 'sbusreg'):
					regresult[tagname] = self._DataTable.GetRegistersInt(memaddr)

				elif (addrtype == 'sbusregstr'):
					strdata = self._ExtData.GetRegStr(memaddr[0], memaddr[1])
					# Strip off any leading or trailing 'null' characters.
					regresult[tagname] = strdata.rstrip(chr(0)).lstrip(chr(0))

				else:
					# This could be a result of a programming error elsewhere.
					dataerrors[tagname] = 'servererror'

			except:
				dataerrors[tagname] = 'addresserror'


		return regresult, dataerrors


	########################################################
	def SetDataValues(self, newdata):
		"""Write the changed values to the data destination. This also
		checks to see if register values will fit in an SBus register,
		and if the register type is writable.
		Params: addrlist (list) - A list of tuples containing tag name, 
			SBus address types, data types, memory address, and data value. 
			E.g. [('PB1', 'sbusflag', 'boolean', 5000, 0), 
				('PB2', 'sbusflag', 'boolean', 4998, 1), 
				('PumpSpeed', 'sbusreg', 'integer', 23, 1800)]
		Returns: (dict) - A dictionary where the keys are the 
			tag names and the values are error codes. If there were no
			errors, the dictionary will be empty.
			E.g. {'PB2' : 'outofrange'}
		"""
		dataerrors = {}		# Errors.

		for tagname, addrtype, datatype, memaddr, datavalue in newdata:

			try:

				if (addrtype == 'sbusflag'):
					# Convert the data value to integer. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = int(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Now, check to see if the values are legal.
					if (datavalue == 0):
						self._DataTable.SetFlagsBool(memaddr, False)
					elif (datavalue == 1):
						self._DataTable.SetFlagsBool(memaddr, True)
					else:
						dataerrors[tagname] = 'badtype'


				elif (addrtype == 'sbusoutput'):
					# Convert the data value to integer. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = int(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Now, check to see if the values are legal.
					if (datavalue == 0):
						self._DataTable.SetOutputsBool(memaddr, False)
					elif (datavalue == 1):
						self._DataTable.SetOutputsBool(memaddr, True)
					else:
						dataerrors[tagname] = 'badtype'

				elif (addrtype == 'sbusreg'):
					# Convert the data value to integer. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = int(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Check if the value is in range for an 
					# SBus register.
					if ((datavalue > 2147483647) or (datavalue < -2147483648)):
						dataerrors[tagname] = 'outofrange'
					else:
						# Store the result in a single register.
						self._DataTable.SetRegistersInt(memaddr, datavalue)


				elif (addrtype == 'sbusregstr'):
					# The string will be padded or truncated as required.
					self._ExtData.SetRegStr(memaddr[0], memaddr[1], datavalue)

				# These data table types are not writable.
				elif (addrtype == 'sbusinput'):
					dataerrors[tagname] = 'writeprotected'

				# This could be the result of a programming error elsewhere.
				else:
					dataerrors[tagname] = 'servererror'

			except:
				dataerrors[tagname] = 'addresserror'


		# Return any errors.
		return dataerrors


############################################################

