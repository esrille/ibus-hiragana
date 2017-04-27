#!/bin/sh
set -e
set -x

aclocal -I m4
automake -a --foreign --copy
autoconf
./configure --enable-maintainer-mode "$@"
