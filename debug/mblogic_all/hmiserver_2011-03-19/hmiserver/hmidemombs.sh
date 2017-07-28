#!/bin/bash
# HMIServerMBS Demo.

# Start up the HMIServer in the background.
./hmiserver/hmiservermbs.py -r 8600 -p 8082 &

# Give it time to start.
sleep 2.0

# Start up the process simulator program.
../demosupport/demosim/demosimmb.py


