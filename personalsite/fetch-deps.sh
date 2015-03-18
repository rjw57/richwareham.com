#!/bin/bash
#
# Simple script to fetch and install assets via bower.

# Find npm
NPM=$(which npm)
if [ -z "$NPM" ]; then
	echo "Could not find npm on PATH. Is is installed?" >&2
	exit 1
fi

# Install required packages
"$NPM" install

# Update path to include npm's "bin" directory
PATH="$(${NPM} bin):$PATH"

# Install bower components
bower install

