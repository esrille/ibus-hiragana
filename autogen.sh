#!/bin/sh -xe

aclocal --force
autopoint --force
automake --add-missing --force-missing --copy
autoconf -f
./configure "$@"
