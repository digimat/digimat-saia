##############################################################################
# Project: 	MBLogic
# Module: 	DLCkTableInstr.py
# Purpose: 	Table functions for a DL Clock-like PLC.
# Language:	Python 2.5
# Date:		06-Nov-2008.
# Ver:		17-Apr-2009.
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin   <m.os.griffin@gmail.com>
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

import DLCkAddrValidate
import DLCkDataTable

##############################################################################


# Used to help unpack registers into boolean ranges.
_UnpackTable = {
'0' : [False, False, False, False],
'1' : [True, False, False, False],
'2' : [False, True, False, False],
'3' : [True, True, False, False],
'4' : [False, False, True, False],
'5' : [True, False, True, False],
'6' : [False, True, True, False],
'7' : [True, True, True, False],
'8' : [False, False, False, True],
'9' : [True, False, False, True],
'A' : [False, True, False, True],
'B' : [True, True, False, True],
'C' : [False, False, True, True],
'D' : [True, False, True, True],
'E' : [False, True, True, True],
'F' : [True, True, True, True]
}


class TableOps:
	"""Various functions including:
	Shift register functions.
	"""

	############################################################
	def __init__(self, booldatatable, boolsequence, boolindex, 
		worddatatable, wordsequence, wordindex):
		"""Parameters: 
		booldatatable (dict) = The boolean data table.
		boolsequence (list) = List of boolean names. This is used to 
			determine the order of the boolean addresses, as the 
			dictionary which forms the data table itself has no order.
		boolindex (dict) = A dictionary relating boolean address labels to
			boolsequence indexes. This is to allow a fast look-up of
			the list index for any address.
		worddatatable (dict) = The word data table.
		wordsequence (list) = List of register names. This is used to 
			determine the order of the registers, as the 
			dictionary which forms the data table itself has no order.
		wordindex (dict) = A dictionary relating word address labels to
			wordsequence indexes. This is to allow a fast look-up of
			the list index for any address.
		"""
		self._BoolDataTable = booldatatable
		self._BoolSequence = boolsequence
		self._BoolIndex = boolindex
		self._WordDataTable = worddatatable
		self._WordSequence = wordsequence
		self._WordIndex = wordindex


	############################################################
	def _GetWordAddrSeq(self, wordstart, wordend):
		"""Find the starting and ending indexes of the word address range.
		We need this as we deal with them as an ordered sequence.
		The addresses must go in increasing order.
		wordstart (string) = Address label for the start of the range.
		wordend (string) = Address label for the end of the range.
		Returns (list) = List of address lables.
		"""
		startindex = self._WordIndex[wordstart]
		endindex = self._WordIndex[wordend]

		return self._WordSequence[startindex : endindex + 1]


	############################################################
	def _GetBoolAddrSeq(self, boolstart, boolend):
		"""Find the starting and ending indexes of the Boolean address range.
		We need this as we deal with them as an ordered sequence.
		The addresses must go in increasing order.
		boolstart (string) = Address label for the start of the range.
		boolend (string) = Address label for the end of the range.
		Returns (list) = List of address lables.
		"""
		startindex = self._BoolIndex[boolstart]
		endindex = self._BoolIndex[boolend]

		return self._BoolSequence[startindex : endindex + 1]

	############################################################
	def Setbits(self, data, startaddr, endaddr):
		"""Set the state of a range of boolean data table addresses.
		data (boolean) = Data value to write.
		startaddr (string) = Address lable for start of range.
		endaddr (string) = Address lable for end of range.
		"""
		# Find the starting and ending indexes of the data table
		# addresses. We need this as we deal with them as an ordered sequence.
		addrseq = self._GetBoolAddrSeq(startaddr, endaddr)

		for i in addrseq:
			self._BoolDataTable[i] = data


	############################################################
	def ShiftRegister(self, data, clock, lastclock, reset, startaddr, endaddr):
		"""Parameters:
		data (boolean) = Data to be shifted into the shift register.
		clock (boolean) = Create transition.
		lastclock (boolean) = State of "clock" on previous scan.
		reset (boolean) = Reset all bits to zero.
		startaddr (string) = Address lable for start of shift register.
		endaddr (string) = Address lable for end of shift register.
		"""

		# Update the start address with the state of the data input.
		self._BoolDataTable[startaddr] = data

		# If clock and reset are both off, there is nothing to do at this point.
		if ((not (clock and not lastclock)) and (not reset)):
			return

		# Find the starting and ending indexes of the control relay
		# addresses. We need this as we deal with them as an ordered sequence.

		startindex = self._BoolIndex[startaddr]
		endindex = self._BoolIndex[endaddr]

		# The direction of shift depends on whether "start" comes
		# before "end" in the data table.
		if (startindex <= endindex):
			addrseq = self._BoolSequence[startindex : endindex + 1]
		else:
			addrseq = self._BoolSequence[endindex : startindex + 1]
			addrseq.reverse()

		# A reset is requested. A reset will override a shift operation,
		# so we return immediately after completing it.
		if reset:
			for i in addrseq:
				self._BoolDataTable[i] = False
			return


		# A shift operation is requested. We tested for a transition above, so
		# the "if" is not strictly necessary.
		if (clock and not lastclock):
			newvalue = data
			for i in addrseq:
				previous = self._BoolDataTable[i]
				self._BoolDataTable[i] = newvalue
				newvalue = previous


	############################################################
	def _GetPtrAddr(self, ptraddr, ptrtype):
		"""Get a pointer address. Pointers are only used by the Copy Single 
		instruction.
		Parameters: 
		ptraddr (string) = The pointer address string. E.g. 'DD[DS12]'
		ptrtype (string) = The type of pointer (DS, DD, DF, DH)
		Returns (string) = The de-referenced address label, or None if error.
			E.g. 'DD27'
		"""

		# Get the DS address which holds the offset.
		try:
			offsetlabel = ptraddr.split('[')[1]
			offsetlabel = offsetlabel.split(']')[0]
		except:
			return None

		# The maximum pointer offset depends on the type of register.
		if (ptrtype == 'DSPtr'):
			maxptr = DLCkDataTable.MAX_DS
			ptrbase = 'DS%s'
		elif (ptrtype == 'DDPtr'):
			maxptr = DLCkDataTable.MAX_DD
			ptrbase = 'DD%s'
		elif (ptrtype == 'DFPtr'):
			maxptr = DLCkDataTable.MAX_DF
			ptrbase = 'DF%s'
		elif (ptrtype == 'DHPtr'):
			maxptr = DLCkDataTable.MAX_DH
			ptrbase = 'DH%s'

		# Now, read the data offset.
		pointeroffset = self._WordDataTable[offsetlabel]
		# If the offset is not out of range, return the address
		# label. Otherwise, return None.
		if ((pointeroffset > 0) and (pointeroffset <= maxptr)):
			return ptrbase % pointeroffset
		else:
			return None



	############################################################
	def CopySingle(self, source, sourcetype, destination, desttype):
		"""Copy a single value from a source to a single destination. 
		This also takes care of any necessary conversions, as well as 
		handling registers, constants, and pointers.
		Parameters:
		source (string) = The address label of data to be copied.
		sourcetype (string) = The type of source (DS, DD, DH, etc.)		
		destination (string) = The address label the data is to be copied to.
		desttype (string) = The type of destination (DS, DD, DH, etc.)
		"""

		# This instruction has special requirements because of the need
		# to handle pointers as well as registers and constants.

		# Reset the system error flags.
		self._BoolDataTable['SC43'] = False
		self._BoolDataTable['SC44'] = False

		# Source is a register.
		if DLCkAddrValidate.IsRegType(sourcetype):
			indata = self._WordDataTable[source]
		# Source is a numeric constant.
		elif DLCkAddrValidate.IsNumericConstType(sourcetype):
			indata = source
		# Source is a text constant.
		elif DLCkAddrValidate.IsTextConstType(sourcetype):
			indata = source
		# Source is a pointer.
		elif DLCkAddrValidate.IsPtrType(sourcetype):
			dataaddr = self._GetPtrAddr(source, sourcetype)
			# Check if the pointer address was valid.
			if (dataaddr == None):
				self._BoolDataTable['SC44'] = True
				return
			else:
				indata = self._WordDataTable[dataaddr]

		# Data is of no known type.
		else:
			self._BoolDataTable['SC44'] = True
			return


		# Destination is a register.
		if DLCkAddrValidate.IsRegType(desttype):
			destinationaddr = destination
		# Destination is a pointer.
		elif DLCkAddrValidate.IsPtrType(desttype):
			destinationaddr = self._GetPtrAddr(destination, desttype)
			# Check if the pointer address was valid.
			if (destinationaddr == None):
				self._BoolDataTable['SC44'] = True
				return
		# Destination is of no known type.
		else:
			self._BoolDataTable['SC44'] = True
			return
		


		# Check if the value converts OK.
		convertedvalue = DLCkAddrValidate.ConvertRegType(sourcetype, desttype, indata)
		if (convertedvalue == None):
			self._BoolDataTable['SC43'] = True
			return

		# Check if the data is within range.
		datarangeOK = DLCkAddrValidate.RangeLimit(desttype, convertedvalue)
		# Set the system flag accordingly.
		self._BoolDataTable['SC43'] = not datarangeOK
		if (not datarangeOK):
			return

		# If the range is OK, convert the type and store it.
		# Text strings need special handling, as they can copy
		# multiple characters at once.
		if DLCkAddrValidate.IsTxtReg(desttype):
			# Is this a multiple register string?
			if (len(convertedvalue) > 1):
				startindex = self._WordIndex[destinationaddr]
				registerspan = len(convertedvalue)
				if (DLCkAddrValidate.RegisterOffset(destinationaddr, registerspan) !=None):
					destseq = self._WordSequence[startindex : startindex + registerspan + 1]
					# Now, copy the source constant string to the destination registers.
					for i in range(len(convertedvalue)):
						self._WordDataTable[destseq[i]] = convertedvalue[i]
				# Attempted to copy beyond the end of the register range.
				else:
					self._BoolDataTable['SC44'] = True
					return
			# If not, this is a simple assignment.
			else:
				self._WordDataTable[destinationaddr] = convertedvalue
			
		# Single register numeric types are a simple assignment.
		else:
			self._WordDataTable[destinationaddr] = convertedvalue




	############################################################
	def CopyFill(self, source, destinationstart, destinationend, desttype):
		"""Copy a single value from a source to a range of destinations. 
		This also takes care of any necessary conversions, as well as handling
		registers and constants.
		Parameters:
		source (any value) = The value to be copied.
		destinationstart (string) = The starting address label the data is to be copied to.
		destinationend (string) = The ending address label the data is to be copied to.
		desttype (string) = The type of destination (DS, DD, DH, etc.)
		"""

		# Reset the system error flags.
		self._BoolDataTable['SC43'] = False
		self._BoolDataTable['SC44'] = False


		# Check if the data is within range.
		datarangeOK = DLCkAddrValidate.RangeLimit(desttype, source)
		# Set the system flag accordingly.
		self._BoolDataTable['SC43'] = not datarangeOK
		if not datarangeOK:
			return

		# Convert the data type.
		datavalue = DLCkAddrValidate.ConvertRegTypeNoSign(desttype, source)
		datavalue = source
		if (datavalue == None):
			self._BoolDataTable['SC43'] = True
			return


		# Find the starting and ending indexes of the register
		# addresses. We need this as we deal with them as an ordered sequence.
		addrseq = self._GetWordAddrSeq(destinationstart, destinationend)

		# Now, copy the data value to all the addresses.
		for i in addrseq:
			self._WordDataTable[i] = datavalue


	############################################################
	def CopyBlock(self, sourcestart, sourceend, destinationstart, desttype):
		"""Copy a block of data from one range of registers to another.
		This also takes care of any necessary conversions, as well as handling
		registers and constants.
		Parameters:
		sourcestart (string) = The starting address label of the data to be copied.
		sourceend (string) = The ending address label of the data to be copied.
		destinationstart (string) = The starting address label the data is to be copied to.
		desttype (string) = The type of destination (DS, DD, DH, etc.)
		"""

		# Reset the system error flags.
		self._BoolDataTable['SC43'] = False
		self._BoolDataTable['SC44'] = False

		# Find the starting and ending indexes of the register source
		# addresses. We need this as we deal with them as an ordered sequence.
		startindex = self._WordIndex[sourcestart]
		endindex = self._WordIndex[sourceend]

		# The addresses must go in order.
		sourceseq = self._WordSequence[startindex : endindex + 1]
		registerspan =  endindex - startindex

		# Repeat for the destination registers.
		startindex = self._WordIndex[destinationstart]
		endindex = startindex + registerspan

		# The addresses must go in order.
		destseq = self._WordSequence[startindex : startindex + registerspan + 1]

		# Now, get a copy of the source registers.
		sourcevalues = []
		for i in sourceseq:
			value = self._WordDataTable[i]
			
			# Check if the data is within range.
			datarangeOK = DLCkAddrValidate.RangeLimit(desttype, value)
			# Set the system flag accordingly.
			self._BoolDataTable['SC43'] = not datarangeOK
			if not datarangeOK:
				return

			# Convert the data type.
			datavalue = DLCkAddrValidate.ConvertRegTypeNoSign(desttype, value)
			datavalue = value

			if (datavalue == None):
				self._BoolDataTable['SC43'] = True
				return

			# Store it in the temporary list.
			sourcevalues.append(datavalue)


		# Now, copy the source registers to the destination registers.
		for i in range(len(sourcevalues)):
			self._WordDataTable[destseq[i]] = sourcevalues[i]


	############################################################
	def CopyPack(self, sourcestart, sourceend, destination):
		"""Pack a block of boolean data into a register.
		Parameters:
		sourcestart (string) = The starting address label of the data to be copied.
		sourceend (string) = The ending address label of the data to be copied.
		destination (string) = The address label the data is to be copied to.
		"""

		# Find the starting and ending indexes of the boolean source
		# addresses. We need this as we deal with them as an ordered sequence.
		# Get a copy of the boolean address sequence.
		sourceseq = self._GetBoolAddrSeq(sourcestart, sourceend)

		# Reverse it so we can deal with the most significant bit first.
		sourceseq.reverse()

		# Now, pack the source bits into an integer.
		value = 0
		for i in sourceseq:
			value <<=1
			value = value | self._BoolDataTable[i]


		# Write the result to the word data table.
		self._WordDataTable[destination] = value


	############################################################
	def CopyUnpack(self, source, destinationstart, destinationend):
		"""Unpack a register into a block of booleans.
		Parameters:
		source (any value) = The value to be unpacked.
		destinationstart (string) = The starting address label the data is to be copied to.
		destinationend (string) = The ending address label the data is to be copied to.
		"""

		# Find the starting and ending indexes of the boolean source
		# addresses. We need this as we deal with them as an ordered sequence.
		# Get a copy of the boolean address sequence.
		destseq = self._GetBoolAddrSeq(destinationstart, destinationend)


		# Get the source value from the word data table.
		value = self._WordDataTable[source]

		# Now, unpack the register into a list. To do this, we first
		# convert it into a string of hex digits, which we use to look up
		# the equivalent values from a dictionary we created for this purpose.
		sourcestr = '%04X' % value
		sourcebits = []
		sourcebits.extend(_UnpackTable[sourcestr[3]])
		sourcebits.extend(_UnpackTable[sourcestr[2]])
		sourcebits.extend(_UnpackTable[sourcestr[1]])
		sourcebits.extend(_UnpackTable[sourcestr[0]])


		# Now, copy the bits into the boolean data table.
		bitpos = 0
		for i in destseq:
			self._BoolDataTable[i] = sourcebits[bitpos]
			bitpos += 1


	############################################################
	def _SearchMatch(self, cmptype, value1, value2):
		""" This is used as part of the Search routine. It compares two 
		values according to a string compare type. It returns True if
		they meet the compare criteria, or False of they don't.
		"""
		if (cmptype == '==') and (value1 == value2):
			return True
		elif (cmptype == '!=') and (value1 != value2):
			return True
		elif (cmptype == '>') and (value1 > value2):
			return True
		elif (cmptype == '>=') and (value1 >= value2):
			return True
		elif (cmptype == '<') and (value1 < value2):
			return True
		elif (cmptype == '<=') and (value1 <= value2):
			return True
		else:
			return False


	############################################################
	def Search(self, searchval, sourcetype, searchstart, searchend, resultaddr, resultflag, compare, incremental):
		"""Search a table of data for a value, and return the location.
		searchval (any value) = The value to search for.
		sourcetype (string) = The type of value to search for. Strings must
			be handled differently than other types.
		searchstart (string) = The data table address to start the search at.
		searchend (string) = The data table address to end the search at.
		resultaddr (string) = The data table word address to store the result in.
		resultflag (string) = The data table boolean address to store the result in.
		compare (string) = The type of search to conduct. '==', '!=', '>', '>=', '<', '<='
		incremental (integer) = 0 means each search starts from the beginning. 1 means
			each search starts from where the last one left off.
		"""

		# Find the starting and ending indexes of the register source
		# addresses. We need this as we deal with them as an ordered sequence.

		lastresult = self._WordDataTable[resultaddr]

		startindex = self._WordIndex[searchstart]
		endindex = self._WordIndex[searchend]

		# If this is an incremental search, we need to start just after the last result.
		if (incremental == 1) and (lastresult > 0) and ((startindex + lastresult) < endindex):
			startoffset = lastresult + 1
			startindex = startindex + startoffset
		else:
			startoffset = 0


		# The addresses must go in order.
		sourceseq = self._WordSequence[startindex : endindex + 1]


		# Search for a match.
		# Check if we are searching for a multi-character string. 
		foundit = False
		if (sourcetype == 'KTxtStr'):
			sourcestr = ''
			# Create a single string from the TXT registers.
			for i in sourceseq:
				sourcestr = '%s%s' % (sourcestr, self._WordDataTable[i])
			# Now, search that string one index at a time.
			searchlen = len(searchval)
			for searchindex in range(len(sourcestr)):
				if self._SearchMatch(compare, sourcestr[searchindex: searchindex + searchlen], searchval):
					foundit = True
					break
		# All other searches operate directly on the appropriate individual registers.
		else:
			searchindex = 0
			for i in sourceseq:
				if self._SearchMatch(compare, self._WordDataTable[i], searchval):
					foundit = True
					break
				# This index is used to keep track of where a match is found.
				searchindex += 1


		# Record the result in the data table.
		self._BoolDataTable[resultflag] = foundit
		if foundit:
			self._WordDataTable[resultaddr] = searchindex + startoffset + 1
		else:
			self._WordDataTable[resultaddr] = -1


	############################################################
	def SumRegisters(self, sourcestart, sourceend, destination, desttype):
		"""Sum the values in a range of registers. This also takes care 
		of any necessary conversions. This also performs a range check
		on the result depending on the destination type and set the
		math flags accordingly.
		Parameters:
		sourcestart (string) = The starting address label of the data.
		sourceend (string) = The ending address label of the data.
		destination (string) = The address label of the destination register.
		desttype (string) = The type of destination (DS, DD, DH, etc.)
		"""

		# Reset the error flag.
		self._BoolDataTable['SC43'] = False

		# Find the starting and ending indexes of the register source
		# addresses. We need this as we deal with them as an ordered sequence.
		# The addresses must go in increasing order.
		sourceseq = self._GetWordAddrSeq(sourcestart, sourceend)

		# Now, sum the source registers.
		value = 0
		for i in sourceseq:
			value += self._WordDataTable[i]

		# Check if the result is within range.
		datarangeOK = DLCkAddrValidate.RangeLimit(desttype, value)
		# Set the system flag accordingly.
		self._BoolDataTable['SC43'] = not datarangeOK
		if not datarangeOK:
			return

		# Convert the data type.
		datavalue = DLCkAddrValidate.ConvertRegTypeNoSign(desttype, value)
		datavalue = value

		if (datavalue == None):
			self._BoolDataTable['SC43'] = True
			return

		# Store the final result.
		self._WordDataTable[destination] = datavalue


	############################################################
	def GetRegString(self, sourcestart, sourceend):
		"""Get the contents of a range of registers and return them
		as a string. This is used for such things as fetching strings
		for compare operations.
		Parameters:
		sourcestart (string) = The starting address label of the data.
		sourceend (string) = The ending address label of the data.
		"""

		# Find the starting and ending indexes of the register source
		# addresses. We need this as we deal with them as an ordered sequence.
		# The addresses must go in increasing order.
		sourceseq = self._GetWordAddrSeq(sourcestart, sourceend)

		# Now, concatenate the source registers.
		regstr = ''
		for i in sourceseq:
			regstr = '%s%s' % (regstr, self._WordDataTable[i])

		return regstr


##############################################################################


