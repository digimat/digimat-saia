##############################################################################
# Project: 	MBLogic
# Module: 	PLCMemSave.py
# Purpose: 	Save selected soft logic data table addresses.
# Language:	Python 2.5
# Date:		18-Apr-2009.
# Ver:		10-Aug-2010.
# Author:	M. Griffin.
# Copyright:	2009 - 2010 - Michael Griffin   <m.os.griffin@gmail.com>
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

import shelve
import time

from mbsoftlogicck import DLCkDataTable

############################################################


class DataTableSave:
	"""Store a selection of data table addresses in a database. This provides 
	persistence of data after a system is shut down and restores the state
	when it is started again.
	"""

	############################################################
	def __init__(self, dbname, datatable):
		"""Parameters: 
		dbname (string) = File name where data table values are saved.
		datatable (dict) = The word data table.
		"""

		# The word data table.
		self._datatable = datatable

		# The file where the data table values are saved.
		self._dbname = dbname

		# Time of last data table update.
		self._lastupdate = time.time()

		# Default update interval.		
		self._updateinterval = -10.0

		# Default list of addresses to save.
		self._monitorlist = []
		# Copy of data table with monitored addresses. This is used to
		# detect when a monitored address has changed.
		self._backingcopy = {}

		# Read in the existing data.
		self._DataTableSaved = shelve.open(self._dbname)

		# Get the existing saved data. If the saved data table file
		# contained names which are not valid data table names, then
		# we ignore them.
		for i in self._DataTableSaved:
			if i in self._datatable:
				self._datatable[i] = self._DataTableSaved[i]


	############################################################
	def __del__(self):
		"""Close the database.
		"""
		try:
			self._DataTableSaved.close()
		except:
			pass	# If not opened, we can't do anything about it.


	############################################################
	def SetSaveParams(self, updateinterval, monitorlist):
		"""Set the parameters for saving data table values.
		Parameters: 
		monitorlist (list) = A list of word data table address keys 
			which are to be monitored.  E.g. ['DS1', 'DD200', 'TXT2345']
		updateinterval (float) = The minimum time in seconds between
			disk updates.
		"""

		# Updates frequencies are limited. We also set a minimum allowed
		# update interval. A negative update interval indicates data table
		# saving is disabled.
		if ((updateinterval > 1.0) or (updateinterval < 0.0)):
			self._updateinterval = updateinterval
		else:
			self._updateinterval = 1.0

		# Save the previous monitor list so we can track any changes.
		oldmonitor = self._monitorlist

		# The list of data table elements to monitor. If an address is 
		# not valid, we simply discard it.
		self._monitorlist = []
		for i in monitorlist:
			if i in self._datatable:
				self._monitorlist.append(i)

		# Now, look for any changes to the monitored list. We look for
		# both addresses that have been added and ones that have been 
		# removed.
		newaddr = list(set(self._monitorlist) - set(oldmonitor))
		removedaddr = list(set(oldmonitor) - set(self._monitorlist))


		# Now, delete the addresses that have been removed.
		for i in removedaddr:
			del self._backingcopy[i]

		# Add in the addresses that have been added. We set he default
		# to None so the change will be detected in the next normal cycle.
		for i in newaddr:
			self._backingcopy[i] = None


	############################################################
	def UpdateData(self):
		"""Save any data table elements which have changed since the
		last time it was checked. Data will be saved only if any
		any of the monitored addresses have changed and if the minimum
		save time interval has passed. If the update interval is
		negative, data table saving is disabled.
		"""
		# Check if the minimum update interval has expired.
		if (((time.time() - self._lastupdate) < self._updateinterval) or
			(self._updateinterval < 0.0)):
			return

		# Time of last disk update.
		self._lastupdate = time.time()

		syncrequired = False
		for i in self._monitorlist:
			if (self._datatable[i] != self._backingcopy[i]):
				self._DataTableSaved[i] = self._datatable[i]
				self._backingcopy[i] = self._datatable[i]
				syncrequired = True


		# If any change has occured, update the disk.
		if syncrequired:
			self._DataTableSaved.sync()


	############################################################
	def PurgeSavedData(self):
		"""Purge unused data from the saved file. This purges any
		data from the disk file which is not in the current list of
		monitored addresses. 
		"""
		# Get a list of existing keys.
		oldkeys = self._DataTableSaved.keys()

		# Get a list of keys which are saved but no longer used.
		purgekeys = list(set(oldkeys) - set(self._monitorlist))

		# Now purge the file of any unused addresses.
		for i in purgekeys:
			del self._DataTableSaved[i]

		# Force updates to disk.
		self._DataTableSaved.sync()


############################################################


########################################################################
class SaveDataTable:
	"""Save the configured data table values to disk.
	"""

	############################################################
	def __init__(self):
		"""
		"""
		# Read in the saved data table values from disk. This restores
		# the configured data table values that were saved the last
		# time the software was run.
		self._DataTableSave = DataTableSave('mblogic.dtable', 
			DLCkDataTable.WordDataTable)

		# This simply wraps the UpdateData method.
		self.UpdateData = self._DataTableSave.UpdateData

	############################################################
	def SetSaveParams(self, updaterate, memsavewordaddr):
		"""Set the data table save parameters.
		Parameters:
		updaterate (float) = The minimum time in seconds between disk updates.
		memsavewordaddr (list) - List of strings representing soft logic data
			table addresses to save.
		"""
		self._DataTableSave.SetSaveParams(updaterate, memsavewordaddr)
		self._DataTableSave.PurgeSavedData()



########################################################################

DataTableSave = SaveDataTable()

########################################################################

