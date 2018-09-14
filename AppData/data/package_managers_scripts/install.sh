#!/bin/bash

# Command to install packages in bulk.
#
# $1 is a list of packages names separated by single spaces.

apt-cache show $1
