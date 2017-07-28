##############################################################################
# Project: 	MBLogic
# Module: 	MBAddrTypes.py
# Purpose: 	Communications and data table address types.
# Language:	Python 2.6
# Date:		19-Jul-2010.
# Ver:		19-Jul-2010.
# Author:	M. Griffin.
# Copyright:	2010 - Michael Griffin       <m.os.griffin@gmail.com>
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

"""This is used to provide a common definition of address types and their
limits. Address types are based on the Modbus definitions, but are extended
to include additional types overlaid on them, as well as data table addresses
which may extend beyond Modbus protocol limits (not all systems are limited
by the Modbus protocol). 

It is important to note that these are *data table* addresses, not Modbus
protocol addresses. The two are not necessarily identical.
"""

########################################################
# Basic Modbus address types and limits. 
MaxBasicAddrTypes = {'coil' : 65535,
		'discrete' : 65535,
		'holdingreg' : 1048575,
		'inputreg' : 65535
		}


# The maximum limits for each address type, including extended
# data types. 
MaxExtAddrTypes = {'coil' : MaxBasicAddrTypes['coil'],
		'discrete' : MaxBasicAddrTypes['discrete'],

		'holdingreg' : MaxBasicAddrTypes['holdingreg'],
		'holdingreg32' : MaxBasicAddrTypes['holdingreg'],
		'holdingregfloat' : MaxBasicAddrTypes['holdingreg'],
		'holdingregdouble' : MaxBasicAddrTypes['holdingreg'],
		'holdingregstr8' : MaxBasicAddrTypes['holdingreg'],
		'holdingregstr16' : MaxBasicAddrTypes['holdingreg'],

		'inputreg' : MaxBasicAddrTypes['inputreg'],
		'inputreg32' : MaxBasicAddrTypes['inputreg'],
		'inputregfloat' : MaxBasicAddrTypes['inputreg'],
		'inputregdouble' : MaxBasicAddrTypes['inputreg'],
		'inputregstr8' : MaxBasicAddrTypes['inputreg'],
		'inputregstr16' : MaxBasicAddrTypes['inputreg']
		}
		

########################################################


