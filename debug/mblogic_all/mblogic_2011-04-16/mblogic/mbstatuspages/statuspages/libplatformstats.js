/** ##########################################################################
# Project: 	MBLogic
# Module: 	libplatformstats.js
# Purpose: 	MBLogic platform data display library.
# Language:	javascript
# Date:		20-Dec-2010
# Ver:		16-Mar-2011
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
**/


// ##################################################################
/* This controls the platform data summary page. 
Parameters: utillib (object) = The utility display library.
*/
function PlatformData(utillib) {

	// Utility library
	this.Utils = utillib;


	// These are values that shouldn't change frequently (or at all).
	this.CheckList = ["system", "platform", "node", "python_version", 
						"python_revision", "memtotal", "cpumodel_name", 
						"disksize", "diskfree"];
	this.LastResult = [];

	for (var index in this.CheckList) {
		this.LastResult[index] = null;
	}

	// CPU load calculation buffer.
	this.CPUTotalBuff = [];
	this.CPUIdlebuff = [];
	this.CPUServerBuff = [];

	// Host name has been updated on the page.
	this.HostDisplayed = false;


	// ##################################################################
	// Update the page results.
	function _UpdatePageResults(pageresults) {
		// Check to see if there have been any changes since the last scan.
		var updated = false;
		for (var index in this.CheckList) {
			if (this.LastResult[index] != pageresults[this.CheckList[index]]) {
				this.LastResult[index] = pageresults[this.CheckList[index]];
				var updated = true;
			}
		}


		// If the platform does not support extended stats, then hide that area
		// of the display table.
		var extendedstats = pageresults['extendedstats'];
		if (extendedstats) {
			this.Utils.ShowPageArea("extendedstats");
		} else {
			this.Utils.HidePageArea("extendedstats");
		}


		// Only update data that changes.
		if (updated) {
			// Fill the tables with data only.
			for (var i in this.CheckList) {
				var fieldname = this.CheckList[i];
				this.Utils.ShowCell(fieldname, pageresults[fieldname]);
			}
		}

		// This will not change.
		if (!this.HostDisplayed) {
			this.Utils.ShowCell("hostaddr", window.location.hostname);
			this.HostDisplayed = true;
		}

		// Default CPU load parameters.
		var cpuload = '';
		var serverload = '';

		// CPU load only applies to extended stats.
		if (extendedstats) {

			// We keep a buffer of CPU load results so we can average them over time.
			this.CPUTotalBuff.push(pageresults['cputotal']);
			this.CPUIdlebuff.push(pageresults['cpuidle']);
			this.CPUServerBuff.push(pageresults['servercpu']);


			// Buffer size limit. All the buffers are in synch, so we only
			// need to check one of them for length.
			// Note: If the checked length is changed, the countdown should 
			// be changed to match.
			var countdown = '***********';
			if (this.CPUTotalBuff.length > 10) {
				this.CPUTotalBuff.shift();
				this.CPUIdlebuff.shift();
				this.CPUServerBuff.shift();

				// Total elapsed time in our averaged period.
				// Don't start calculating until we have a long enough time base.
				var buffsize = this.CPUTotalBuff.length;
				if (buffsize > 3) {
					try {
						// This tracks the elapsed time.
						var timediff = this.CPUTotalBuff[buffsize - 1] - this.CPUTotalBuff[0]
						// Total average load. We are converting idle time to usage, so we need to subtract from 100%
						var loadcalc = 100.0 - (((this.CPUIdlebuff[buffsize - 1] - this.CPUIdlebuff[0]) / timediff) * 100.0);
						var cpuload = loadcalc.toFixed(1);
						// Load used by the server.
						var servercalc = ((this.CPUServerBuff[buffsize - 1] - this.CPUServerBuff[0]) / timediff) * 100.0;
						var serverload = servercalc.toFixed(1);

						// Negative values can be caused by a server restart, which invalidates 
						// the buffered data.
						if ((cpuload < 0) | (serverload < 0)) {
							var cpuload = '';
							var serverload = '';
							this.CPUTotalBuff = [];
							this.CPUIdlebuff = [];
							this.CPUServerBuff = [];
						}

					// Null values will cause an error. This will probably be due to 
					// the server platform not supporting these additional stats.
					} catch (d) {
						var cpuload = '';
						var serverload = '';
					}
				}
			} else {
				// This provides a "countdown" symbol view while waiting for numbers.
				var cpuload = countdown.substr(this.CPUTotalBuff.length);
				var serverload = cpuload;
			}

		}

		// Show the CPU loads.
		this.Utils.ShowCell("cpupercent", cpuload);
		this.Utils.ShowCell("servercpu", serverload);


	}
	this.UpdatePageResults = _UpdatePageResults;
}

