##############################################################################
# Project: 	Modbus Library
# Module: 	MBDataTable.py
# Purpose: 	Modbus TCP Server (slave).
# Language:	Python 2.5
# Date:		21-Apr-2008.
# Ver:		07-Jun-2009.
# Author:	M. Griffin.
# Copyright:	2008 - 2009 - Michael Griffin       <m.os.griffin@gmail.com>
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

from mbprotocols import ModbusMemTable
from mbprotocols import ModbusExtData

##############################################################################
"""
This module creates the Modbus memory map (data table) to allow it to be 
directly imported into the various services. This is a global program resource 
with only once instance which is why ModbusMemTable can't be created multiple 
times. The structure of the Twisted server prevents creating it in the main 
module and passing to the various server protocol implementations.

Also created is an object for storing and retrieving extended data types 
(multi-register) in a Modbus data table.
"""

# Create the data table.
MemMap = ModbusMemTable.ModbusMemTable()

# Extended data types.
MemExtData = ModbusExtData.ExtendedDataTypes(MemMap)

