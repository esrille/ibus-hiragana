#!/bin/sh
set -e
set -x

aclocal
automake --add-missing --copy
autoconf
./configure "$@"
