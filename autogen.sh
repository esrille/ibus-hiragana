#!/bin/sh
set -e
set -x

aclocal --force
autopoint --force
automake --add-missing --force-missing --copy
autoconf -f
./configure "$@"
