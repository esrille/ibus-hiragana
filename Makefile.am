# Copyright (c) 2017-2024 Esrille Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# po must be after the directories that contain .desktop files
SUBDIRS = \
	dic \
	docs \
	engine \
	icons \
	layouts \
	setup \
	po \
	$(NULL)

EXTRA_DIST = \
	debian/changelog \
	debian/changelog.in \
	debian/compat \
	debian/control \
	debian/copyright \
	debian/ibus-hiragana.docs \
	debian/rules \
	debian/source/format \
	autogen.sh \
	@PACKAGE_NAME@.spec \
	@PACKAGE_NAME@.spec.in \
	CONTRIBUTING.md \
	LICENSE \
	NOTICE \
	README.md \
	README.txt \
	$(NULL)

DISTCLEANFILES = \
	po/stamp-it \
	$(NULL)

debian/changelog:
	$(AM_V_GEN) \
	( \
		date=`date -R`; \
		version=@VERSION@; \
		source_version=@SOURCE_VERSION@; \
		s=`cat debian/changelog.in`; \
		eval "echo \"$${s}\""; \
	) > $@

@PACKAGE_NAME@.spec:
	$(AM_V_GEN) \
	( \
		date=`date '+%a %b %d %Y'`; \
		version=@VERSION@; \
		source_version=@SOURCE_VERSION@; \
		s=`cat @PACKAGE_NAME@.spec.in`; \
		eval "echo \"$${s}\""; \
	) > $@

uninstall-hook:
	-rmdir $(pkgdatadir)

# Remove extra files not in the git repository except
# ibus-hiragana.spec and debian/changelog.
dist-hook:
	rm -f $(distdir)/ABOUT-NLS
	rm -f $(distdir)/Makefile.in
	rm -f $(distdir)/aclocal.m4
	rm -f $(distdir)/compile
	rm -f $(distdir)/config.guess
	rm -f $(distdir)/config.rpath
	rm -f $(distdir)/config.sub
	rm -f $(distdir)/configure
	rm -f $(distdir)/dic/Makefile.in
	rm -f $(distdir)/docs/Makefile.in
	rm -f $(distdir)/engine/Makefile.in
	rm -f $(distdir)/icons/Makefile.in
	rm -f $(distdir)/install-sh
	rm -f $(distdir)/layouts/Makefile.in
	rm -f $(distdir)/missing
	rm -f $(distdir)/po/Makefile.in.in
	rm -f $(distdir)/po/Rules-quot
	rm -f $(distdir)/po/boldquot.sed
	rm -f $(distdir)/po/en@boldquot.header
	rm -f $(distdir)/po/en@quot.header
	rm -f $(distdir)/po/insert-header.sin
	rm -f $(distdir)/po/ja.gmo
	rm -f $(distdir)/po/quot.sed
	rm -f $(distdir)/po/remove-potcdate.sin
	rm -f $(distdir)/po/stamp-po
	rm -f $(distdir)/py-compile
	rm -f $(distdir)/setup/Makefile.in
