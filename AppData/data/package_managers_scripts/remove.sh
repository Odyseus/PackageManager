#!/bin/bash

# Command to remove/uninstall packages in bulk.
#
# $1 is a list of packages names separated by single spaces.

apt-cache show $1
