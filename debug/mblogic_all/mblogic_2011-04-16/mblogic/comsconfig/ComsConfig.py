##############################################################################
# Project: 	MBLogic
# Module: 	ComsConfig.py
# Purpose: 	Read configuration data for communications.
# Language:	Python 2.5
# Date:		07-Mar-2008.
# Version:	17-Oct-2010.
# Author:	M. Griffin.
# Copyright:	2008 - 2010 - Michael Griffin       <m.os.griffin@gmail.com>
# Modified by: Juan Pomares <pomaresj@gmail.com>
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


import ConfigCommsServer, ConfigCommsClient

# Server and client config file names.
_ServerConfigFile = 'mbserver.config'
_ClientConfigFile = 'mbclient.config'

# Create the configuration object.
ConfigServer = ConfigCommsServer.CommsConfig(_ServerConfigFile)
# Parse the configuration file.
ConfigServer.GetConfig()

# This is used only for saving edited configurations. We *don't*
# use it to read the configuration file from disk.
def SaveConfigServer(newconfig):
	saveserver = ConfigCommsServer.CommsConfig(_ServerConfigFile)
	return saveserver.SetServerConfig(newconfig)



# Create the configuration object.
ConfigClient = ConfigCommsClient.CommsConfig(_ClientConfigFile)
# Parse the configuration file.
ConfigClient.GetConfig()

# This is used only for saving edited configurations. We *don't*
# use it to read the configuration file from disk.
def SaveConfigClient(newconfig):
	saveclient = ConfigCommsClient.CommsConfig(_ClientConfigFile)
	return saveclient.SetClientConfig(newconfig)



