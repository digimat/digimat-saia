##############################################################################
# Project: 	MBLogic
# Module: 	PlatformStats.py
# Purpose: 	Reports platform statistics.
# Language:	Python 2.6
# Date:		20-Dec-2010.
# Version:	16-Apr-2011.
# Author:	M. Griffin.
# Copyright:	2010 - 2011 - Michael Griffin       <m.os.griffin@gmail.com>
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
"""
This module is used to calculate and display various platform statistics.
"""
############################################################

import time
import os
import platform

# The resource module is not present on MS Windows.
try:
	import resource
	resourceok = True
except:
	resourceok = False

# We have to import it like this to avoid coliding with the standard 
# Python module of the same name.
import twisted.web.resource

import MonUtils

############################################################

class PlatformStats:
	"""Read and return the available platform statistics.
	"""

	########################################################
	def __init__(self):
		# 1073741824 is a "binary" gigabyte.
		self._Gigabyte = 1073741824.0

		# Last time the disk stats were updated.
		self._LastTime = 0.0

		# Default string for when we have an error getting data.
		self._DefaultErrorStr = '?????'

		# Default data.
		self._Stats = {'system' : platform.system(),
			'platform' : platform.platform(),
			'node' : platform.node(),
			'python_version' : platform.python_version(),
			'python_revision' : platform.python_revision(),

			'extendedstats' : False,

			'memtotal' : None,
			'cpumodel_name' : None,
			'disksize' : None,

			'cputotal' : None,
			'cpuidle' : None,
			'servercpu' : None,
			'diskfree' : None
		}

		# The following information is platform specific, but it won't
		# change during run time.
		if platform.system() == 'Linux':

			# Extended stats are available.
			self._Stats['extendedstats'] = True

			# We extract the total amount of installed memory.
			try:
				with open('/proc/meminfo') as f:
					meminfo = f.readlines()
					# Find the line with the total memory.
					memtotalstr = [x for x in meminfo if x.lower().startswith('memtotal:')]
					# Split the field on the first ":" character, get 
					# the second half, and strip the leading and trailing blanks.
					self._Stats['memtotal'] = memtotalstr[0].split(':', 1)[1].strip()
			except:
				self._Stats['memtotal'] = self._DefaultErrorStr

			# We extract the model (name) of CPU.
			try:
				with open('/proc/cpuinfo') as f:
					cpuinfo = f.readlines()
					#model_namestr = filter(lambda x: x.startswith('model name'), cpuinfo)
					# See if we can find the model name.
					model_namestr = [x for x in cpuinfo if x.lower().startswith('model name')]
					# No? Perhaps this is an ARM board using the "processor" for this.
					if len(model_namestr) == 0:
						model_namestr = [x for x in cpuinfo if x.lower().startswith('processor')]
					modelstr = model_namestr[0].split(':', 1)[1].strip()

					# If this can be successfully converted to an integer, it 
					# isn't really a CPU name. This problem may arise with ARM.
					# If everything *is* OK, then we should get an exception.
					try:
						cpuint = int(modelstr)
						modelstr = self._DefaultErrorStr
					except:
						pass

					self._Stats['cpumodel_name'] = modelstr
			except:
					self._Stats['cpumodel_name'] = self._DefaultErrorStr

			# Disk size.
			try:
				diskstats = os.statvfs('/home')
				self._Stats['disksize'] = '%.1f GB' % ((diskstats.f_bsize * diskstats.f_blocks) / self._Gigabyte)
			except:
				self._Stats['disksize'] = self._DefaultErrorStr



	########################################################
	def GetStatus(self):
		"""Read and return the available platform statistics.
		"""
		# Typical is: 
		# {'system' : 'Linux', 'node' : 'plant-pc5', 
		# 'platform' : 'Linux-2.6.32-26-generic-x86_64-with-Ubuntu-10.04-lucid',
		# 'python_version' : '2.6.5', 'python_revision' : '79063',
		# 'cputotal' : 26223.06, 'cpuidle' : 22702.34,
		# 'memtotal' : '4115008 kB', 'model_name' : 'AMD SuperDuper 6800+',
		# 'disksize' : '250.1 GB', 'diskfree' : '75.9 GB',
		# 'servercpu' : 211.14}


		# These stats are platform specific and variable.
		if self._Stats['system'] == 'Linux':
			# Extract the total CPU time and the idle time.
			# We can calculate the CPU percentage from consecutive calls.
			try:
				with open('/proc/uptime') as f:
					uptimestr = f.read()
					uptime = uptimestr.split()
					self._Stats['cputotal'] = float(uptime[0])
					self._Stats['cpuidle'] = float(uptime[1])
			except:
				self._Stats['cputotal'] = 0
				self._Stats['cpuidle'] = 0

			# The resource module should be available, but we'll check anyway.
			try:
				if resourceok:
					parentcpu = resource.getrusage(resource.RUSAGE_SELF)
					self._Stats['servercpu'] = parentcpu.ru_utime + parentcpu.ru_stime
				else:
					self._Stats['servercpu'] = 0
			except:
				self._Stats['servercpu'] = 0

			# Disk free space. We only repeat this calculation if a defined
			# interval has passed. 
			currenttime = time.time()
			if (currenttime - self._LastTime > 60.0):
				try:
					self._LastTime = currenttime
					diskstats = os.statvfs('/home')
					self._Stats['diskfree'] = '%.1f GB' % ((diskstats.f_bsize * diskstats.f_bavail) / self._Gigabyte)
				except:
					self._Stats['diskfree'] = self._DefaultErrorStr


		# Return the completed stats.
		return self._Stats


_PlatformStats = PlatformStats()

############################################################
class SimpleResponse(twisted.web.resource.Resource):
	"""Serve Javscript files which are generated dynamically to contain
	the current status data. 
	"""

	isLeaf = True	# This is a resource end point.

	########################################################
	def __init__(self, sourcedata):
		"""Initialise with the function to call to fetch the data.
		"""
		self._source = sourcedata

	########################################################
	# Return the page for a GET. This will handle requests
	# to read data.
	def render_GET(self, request):

		# Errors will return an HTTP error code.
		try:
			# Get the data and encode it.
			reportdata = MonUtils.JSONEncode(self._source())
		except:
			request.setResponseCode(404)
			reportdata = ''

		# Send the headers.
		request.setHeader('content-type', 'application/json')
		# Send the page.
		return reportdata


############################################################

# Platform statistics.
PlatformStatsResponse = SimpleResponse(_PlatformStats.GetStatus)


