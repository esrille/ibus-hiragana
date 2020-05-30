#!/bin/sh
set -e
set -x

aclocal
autopoint
automake --add-missing --copy
autoconf
./configure "$@"
