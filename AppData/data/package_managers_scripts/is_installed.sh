#!/bin/bash

# Command to check if a single package is installed in a system.
#
# $1 is the name of a single package.

dpkg -l $1
