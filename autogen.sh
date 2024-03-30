#!/bin/sh -xe
autoreconf -fi -v
./configure "$@"
