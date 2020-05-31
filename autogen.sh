#!/bin/sh
set -e
set -x

aclocal
autopoint --force
automake --add-missing --copy
autoconf
./configure "$@"
