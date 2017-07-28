##############################################################################
# Project: 	MBLogic
# Module: 	DLCkDataTable.py
# Purpose: 	Define data table for a DL Click-like PLC.
# Language:	Python 2.5
# Date:		31-Oct-2008.
# Ver:		08-Jun-2009.
# Author:	M. Griffin.
# Copyright:	2008 - Michael Griffin   <m.os.griffin@gmail.com>
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

import PLCStdMem

############################################################
"""
This module creates the data tables used by the soft logic system. This 
implementation is necessarily specific to the model of PLC being emulated.
"""


# Control relay, timer, and counter addresses. We need these separately from 
# the other boolean addresses so we can reference them directly in some instructions. 
TimerAddr = ('T', 1, 500)		# Timer status	
CounterAddr = ('CT', 1, 250)		# Counter status	
TimerData = ('TD', 1, 500)		# Timer current value	Integer
CounterData = ('CTD', 1, 250)		# Counter current value	Double integer


TimerAddrList = PLCStdMem.GenDecimalAddr(TimerAddr[1], TimerAddr[2], TimerAddr[0])
TimerDataList = PLCStdMem.GenDecimalAddr(TimerData[1], TimerData[2], TimerData[0])

CounterAddrList = PLCStdMem.GenDecimalAddr(CounterAddr[1], CounterAddr[2], CounterAddr[0])
CounterDataList = PLCStdMem.GenDecimalAddr(CounterData[1], CounterData[2], CounterData[0])

# Create the rest of the boolean addresses.
ClickBooleanAddr = [
('X', 1, 2000),		# Inputs - This is an extension beyond the "Click" range.
('Y', 1, 2000),		# Outputs - This is an extension beyond the "Click" range.
('C', 1, 2000),		# Control relays
('SC', 1, 1000)		# System control	
]

# This will generate an ordered list of boolean addresses.
BoolAddrList = []
for i in ClickBooleanAddr:
	BoolAddrList.extend(PLCStdMem.GenDecimalAddr(i[1], i[2], i[0]))
# Add the control relays, timers, and counters.
BoolAddrList.extend(TimerAddrList)
BoolAddrList.extend(CounterAddrList)

# This is the boolean data table. All boolean data is stored here.
BoolDataTable = PLCStdMem.GenBoolTable(BoolAddrList)

# This is a dictionary that relates boolean address lables to boolean address label 
# list indexes. This allows a fast look-up of list indexes given an address 
# label. This is used for instruction table operations which work on a 
# sequence of addresses.
BoolAddrIndex = PLCStdMem.GenTableIndex(BoolAddrList)

############################################################

# These values are exported to allow other instructions to know the maximum sizes
# of the data tables. However, the address validators may not necessarily use 
# these numbers directly in their regular expression strings, so they have to 
# be handled separately.

MAX_DS = 10000
MAX_DD = 2000
MAX_DF = 2000
MAX_DH = 2000
MAX_TXT = 10000

############################################################

# Word addresses. XD and YD exist in the word table for compatibility reasons, 
# but are separate address spaces and don't reflect the X and Y boolean addresses. 
# XS and YS provide an equivalent as signed integer.
# The DS, DD, DH, DF and TXT data tables are all extended beyond the
# range described in the DL Click documents.
ClickWordAddr = [
('XD', 1, 125),		# Input register	Unsigned integer
('YD', 1, 125),		# Input register	Unsigned integer
('XS', 1, 125),		# Input register	Signed integer
('YS', 1, 125),		# Input register	Signed integer
('DS', 1, MAX_DS),	# Data register		Integer
('DD', 1, MAX_DD),	# Data register		Double integer
('DH', 1, MAX_DH),	# Data register		Unsigned integer
('SD', 1, 1000),	# System data		Integer
('TD', 1, 500),		# Timer current value	Integer
('CTD', 1, 250)		# Counter current value	Double integer
]

# These need to be separate as their base data types are different.
ClickFloatAddr = ('DF', 1, MAX_DF)	# Data register		Floating point
ClickStrAddr = ('TXT', 1, MAX_TXT)	# Text data		ASCII


# This will generate an ordered list of word addresses.
WordAddrList = []
for i in ClickWordAddr:
	WordAddrList.extend(PLCStdMem.GenDecimalAddr(i[1], i[2], i[0]))

# Add in the floating point and string addresses.
FloadAddrList = PLCStdMem.GenDecimalAddr(ClickFloatAddr[1], ClickFloatAddr[2], ClickFloatAddr[0])
WordAddrList.extend(FloadAddrList)
StrAddrList = PLCStdMem.GenDecimalAddr(ClickStrAddr[1], ClickStrAddr[2], ClickStrAddr[0])
WordAddrList.extend(StrAddrList)

# Add in the timer and counter data lists.
WordAddrList.extend(TimerDataList)
WordAddrList.extend(CounterDataList)

# This is the word data table. All word data is stored here.
WordDataTable = PLCStdMem.GenWordTable(WordAddrList, 0)

# Generate the floating point and string tables.
FloatTable = PLCStdMem.GenWordTable(FloadAddrList, 0.0)
StrTable = PLCStdMem.GenWordTable(StrAddrList, chr(0))

# Now, substitute in the correct data types for the floating point and string addresses.
WordDataTable.update(FloatTable)
WordDataTable.update(StrTable)

# This is a dictionary that relates word address lables to word address label 
# list indexes. This allows a fast look-up of list indexes given an address 
# label. This is used for instruction table operations which work on a 
# sequence of addresses.
WordAddrIndex = PLCStdMem.GenTableIndex(WordAddrList)

############################################################
# Instruction data table.
# This is used by some instructions to store data outside of the normal 
# data tables. Keys are added by the compiler based on an instruction
# index which is generated at compile time. A typical use for this is to store 
# last state information for boolean differentiating instructions which do
# not store information in the normal boolean data table. 

InstrDataTable = {}

############################################################

# Accumulator. This is used for math instructions. This only exists
# as a placeholder to satisfy the interpreter, as this model of PLC 
# doesn't use an accumulator.
Accumulator = None

# This exists only to provide a place holder.
PLCWordTableAccessors = None


