#!/bin/bash

# Command to check if a single package exists in the software sources.
#
# $1 is the name of a single package.

apt-cache show $1
