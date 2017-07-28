#!/bin/bash
# This script starts up MBLogic.

# An exit code of 8 means a request to restart.
ExitCode=119
until [ $ExitCode -ne 119 ]; do
	./mblogic/mbmain.py
	ExitCode=$?
	if [ $ExitCode -eq 8 ]; then
		sleep 4
	fi
	
done

