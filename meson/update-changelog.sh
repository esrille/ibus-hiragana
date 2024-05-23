#!/bin/bash -e

version=$1
source_version=`echo -n $version | tr '~' '-'`

LC_TIME=C

if [ -v MESON_DIST_ROOT ]; then
    cd $MESON_DIST_ROOT
fi

# update spec
date=`date -R`
s=`cat debian/changelog.in`
eval "echo \"$s\"" > debian/changelog

# update changelog
date=`date '+%a %b %d %Y'`
s=`cat ibus-hiragana.spec.in`
eval "echo \"$s\"" > ibus-hiragana.spec
