##############################################################################
# Project: 	HMIServer
# Module: 	SBAddrTypes.py
# Purpose: 	Communications and data table address types.
# Language:	Python 2.6
# Date:		19-Jul-2010.
# Ver:		25-Nov-2010.
# Author:	M. Griffin.
# Copyright:	2010 - Michael Griffin       <m.os.griffin@gmail.com>
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# Important:	WHEN EDITING THIS FILE, USE TABS TO INDENT - NOT SPACES!
##############################################################################

"""This is used to provide a common definition of address types and their
limits. Address types are based on the SBus definitions, but are extended
to include additional types overlaid on them, as well as data table addresses
which may extend beyond SBus protocol limits (not all systems are limited
by the SBus protocol). 

It is important to note that these are *data table* addresses, not SBus
protocol addresses. The two are not necessarily identical.


This version is for HMIServer!!! Unlike MBLogic soft logic, we do not extend
the holding registers address range.
"""

########################################################
# Basic SBus address types and limits. 
MaxBasicAddrTypes = {'sbusflag' : 65535,
		'sbusinput' : 65535,
		'sbusoutput' : 65535,
		'sbusreg' : 65535,
		'sbusregstr' : 65535
		}


# The maximum limits for each address type, including extended
# data types. 
MaxExtAddrTypes = {'sbusflag' : MaxBasicAddrTypes['sbusflag'],
		'sbusinput' : MaxBasicAddrTypes['sbusinput'],
		'sbusoutput' : MaxBasicAddrTypes['sbusoutput'],
		'sbusreg' : MaxBasicAddrTypes['sbusreg'],
		'sbusregstr' : MaxBasicAddrTypes['sbusregstr']
		}
		

########################################################


