##############################################################################
# Project: 	MBLogic
# Module: 	HMIDataTable.py
# Purpose: 	Pass HMI requests on to a Modbus type data table.
# Language:	Python 2.5
# Date:		09-May-2009.
# Ver.:		22-Dec-2009.
# Copyright:	2009 - Michael Griffin       <m.os.griffin@gmail.com>
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

"""This module converts HMI read and write requests into Modbus type data table. 
"""

############################################################

from mbprotocols import ModbusExtData

############################################################


############################################################

class HMIDataTable:
	"""Provide methods for reading and writing a Modbus type data table. These
	are used by higher HMI data handling routines to process HMI messages.
	"""


	########################################################
	def __init__(self, datatable):
		"""datatable (object) = An object which provides methods for
		reading and writing the data table. The ones expected are:
		1) GetCoilsBool = Read a single coil.
		2) GetDiscreteInputsBool = Read a single discrete input.
		3) GetHoldingRegistersInt = Read a single holding register.
		4) GetInputRegistersInt = Read a single input register.
		5) SetCoilsBool = Write to a single coil.
		6) SetHoldingRegistersInt = Write to a single holding register.

		Routines to access extended data types are handled through a
		separate object, which is given a reference to the same data table.
		"""
		self._DataTable = datatable
		# This handles extended data types. These are data types which 
		# span several adjacent registers.
		self._ExtData = ModbusExtData.ExtendedDataTypes(self._DataTable)


	########################################################
	def GetEventStates(self, eventlist):
		"""Get the current states of a list of events.
		Params: eventlist (list) - a list of Modbus coil addresses.
			E.g. [23, 100, 52]
		Returns: (dict) - A dictionary where Modbus coils addresses are
			keys, and the states are boolean values.
			E.g. {23 : 0, 100 : 1, 52 : 1}
		"""
		result = {}
		for i in eventlist:
			result[i] = self._DataTable.GetCoilsBool(i)
		return result

	########################################################
	def GetAlarmStates(self, alarmlist):
		"""Get the current states of a list of alarms.
		Params: eventlist (list) - a list of Modbus coil addresses.
			E.g. [23, 100, 52]
		Returns: (dict) - A dictionary where Modbus coils addresses are
			keys, and the states are boolean values.
			E.g. {23 : 0, 100 : 1, 52 : 1}
		"""
		result = {}
		for i in alarmlist:
			result[i] = self._DataTable.GetCoilsBool(i)
		return result


	########################################################
	def AddressWritable(self, addrtype):
		"""This is used to test if the address type is writable.
		Returns 'writeable' if the address type is writable. 
		Returns 'writeprotected' if the address type is not writable.
		Returns 'unknown' if the address type is unknown.
		"""
		if addrtype in ['coil', 'holdingreg', 'holdingreg32', 'holdingregfloat', 
					'holdingregdouble', 'holdingregstr8', 'holdingregstr16']:
			return 'writeable'
		elif addrtype in ['discrete', 'inputreg',  'inputreg32', 'inputregfloat', 
						'inputregdouble', 'inputregstr8', 'inputregstr16']:
			return 'writeprotected'
		else:
			return 'unknown'


	########################################################
	def GetDataValues(self, addrlist):
		"""Get the current values from the data source.
		Params: addrlist (list) = A list of tuples containing tag name, 
			Modbus address types, data types, and memory addresses. 
			E.g. [('PB1', 'coil', 'boolean', 5000), 
				('PB2', 'coil', 'boolean', 4998), 
				('PumpSpeed', 'holdingreg', 'integer', 23)]
		Returns: (dict), (dict) = Two dictionary where the keys are the 
			tag names. The first dictionary contains any successful read
			results. The second contains error codes.
			E.g. {'PB1' : 1, 'PumpSpeed' : 1825}, {'PB2' : 'addresserror'}
		"""
		regresult = {}		# Register data.
		dataerrors = {}		# Errors.

		for tagname, addrtype, datatype, memaddr in addrlist:
			try:
				if (addrtype == 'coil'):
					regresult[tagname] = int(self._DataTable.GetCoilsBool(memaddr))

				elif (addrtype == 'discrete'):
					regresult[tagname] = int(self._DataTable.GetDiscreteInputsBool(memaddr))

				elif (addrtype == 'holdingreg'):
					regresult[tagname] = self._DataTable.GetHoldingRegistersInt(memaddr)

				elif (addrtype == 'inputreg'):
					regresult[tagname] = self._DataTable.GetInputRegistersInt(memaddr)

				elif (addrtype == 'holdingreg32'):
					regresult[tagname] = self._ExtData.GetHRegInt32(memaddr)

				elif (addrtype == 'inputreg32'):
					regresult[tagname] = self._ExtData.GetInpRegInt32(memaddr)

				elif (addrtype == 'holdingregfloat'):
					regresult[tagname] = self._ExtData.GetHRegFloat32(memaddr)

				elif (addrtype == 'inputregfloat'):
					regresult[tagname] = self._ExtData.GetInpRegFloat32(memaddr)

				elif (addrtype == 'holdingregdouble'):
					regresult[tagname] = self._ExtData.GetHRegFloat64(memaddr)

				elif (addrtype == 'inputregdouble'):
					regresult[tagname] = self._ExtData.GetInpRegFloat64(memaddr)

				elif (addrtype == 'holdingregstr8'):
					strdata = self._ExtData.GetHRegStr8(memaddr[0], memaddr[1])
					# Strip off any leading or trailing 'null' characters.
					regresult[tagname] = strdata.rstrip(chr(0)).lstrip(chr(0))

				elif (addrtype == 'holdingregstr16'):
					strdata = self._ExtData.GetHRegStr16(memaddr[0], memaddr[1])
					# Strip off any leading or trailing 'null' characters.
					regresult[tagname] = strdata.rstrip(chr(0)).lstrip(chr(0))

				elif (addrtype == 'inputregstr8'):
					strdata = self._ExtData.GetInpRegStr8(memaddr[0], memaddr[1])
					# Strip off any leading or trailing 'null' characters.
					regresult[tagname] = strdata.rstrip(chr(0)).lstrip(chr(0))

				elif (addrtype == 'inputregstr16'):
					strdata = self._ExtData.GetInpRegStr16(memaddr[0], memaddr[1])
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
		checks to see if register values will fit in a Modbus register,
		and if the register type is writable.
		Params: addrlist (list) - A list of tuples containing tag name, 
			Modbus address types, data types, memory address, and data value. 
			E.g. [('PB1', 'coil', 'boolean', 5000, 0), 
				('PB2', 'coil', 'boolean', 4998, 1), 
				('PumpSpeed', 'holdingreg', 'integer', 23, 1800)]
		Returns: (dict) - A dictionary where the keys are the 
			tag names and the values are error codes. If there were no
			errors, the dictionary will be empty.
			E.g. {'PB2' : 'outofrange'}
		"""
		dataerrors = {}		# Errors.

		for tagname, addrtype, datatype, memaddr, datavalue in newdata:

			try:

				if (addrtype == 'coil'):
					# Convert the data value to integer. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = int(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Now, check to see if the values are legal.
					if (datavalue == 0):
						self._DataTable.SetCoilsBool(memaddr, False)
					elif (datavalue == 1):
						self._DataTable.SetCoilsBool(memaddr, True)
					else:
						dataerrors[tagname] = 'badtype'

				elif (addrtype == 'holdingreg'):
					# Convert the data value to integer. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = int(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Check if the value is in range for a 
					# Modbus register.
					if ((datavalue > 32767) or (datavalue < -32768)):
						dataerrors[tagname] = 'outofrange'
					else:
						# Store the result in a single register.
						self._DataTable.SetHoldingRegistersInt(memaddr, datavalue)

				elif (addrtype == 'holdingreg32'):
					# Convert the data value to integer. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = int(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Check if the value is in range for a 
					# Modbus register.
					if ((datavalue > 2147483647) or (datavalue < -2147483648)):
						dataerrors[tagname] = 'outofrange'
					else:
						# Store the result in a pair of registers.
						self._ExtData.SetHRegInt32(memaddr, datavalue)

				elif (addrtype == 'holdingregfloat'):
					# Convert the data value to float. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = float(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Store the result in a pair of registers.
					try:
						self._ExtData.SetHRegFloat32(memaddr, datavalue)
					except:
						dataerrors[tagname] = 'outofrange'
						continue


				elif (addrtype == 'holdingregdouble'):
					# Convert the data value to floating point. If it won't convert, 
					# this is an error that must be reported.
					try:
						datavalue = float(datavalue)
					except:
						dataerrors[tagname] = 'badtype'
						continue

					# Store the result in 4 consecutive registers.
					try:
						self._ExtData.SetHRegFloat64(memaddr, datavalue)
					except:
						dataerrors[tagname] = 'outofrange'
						continue


				elif (addrtype == 'holdingregstr8'):
					# The string will be padded or truncated as required.
					self._ExtData.SetHRegStr8(memaddr[0], memaddr[1], datavalue)

				elif (addrtype == 'holdingregstr16'):
					# The string will be padded or truncated as required.
					self._ExtData.SetHRegStr16(memaddr[0], memaddr[1], datavalue)

				# These data table types are not writable.
				elif (addrtype  in ['discrete', 'inputreg']):
					dataerrors[tagname] = 'writeprotected'

				# This could be the result of a programming error elsewhere.
				else:
					dataerrors[tagname] = 'servererror'

			except:
				dataerrors[tagname] = 'addresserror'


		# Return any errors.
		return dataerrors


############################################################

