## Process this file with automake to produce Makefile.in
## Created by Anjuta

SUBDIRS = src desktop po conf

vox_launcherdocdir = ${prefix}/doc/vox-launcher
vox_launcherdoc_DATA = \
	README\
	COPYING\
	AUTHORS\
	ChangeLog\
	INSTALL\
	NEWS


INTLTOOL_FILES = intltool-extract.in \
	intltool-merge.in \
	intltool-update.in

EXTRA_DIST = config.rpath m4/ChangeLog  $(vox_launcherdoc_DATA) \
	$(INTLTOOL_FILES)

DISTCLEANFILES = intltool-extract \
	intltool-merge \
	intltool-update \
	po/.intltool-merge-cache


# Remove doc directory on uninstall
uninstall-local:
	-rm -r $(vox_launcherdocdir)

ACLOCAL_AMFLAGS = -I m4

deb:
	@if test -s "`which debuild`"; then                                                \
                debuild -us -uc -b;                                                        \
                mv ../$(PACKAGE_NAME)_$(PACKAGE_VERSION)*.deb .;                        \
        else                                                                               \
                echo "You need to install the debian package 'devscripts'";                \
                exit 1;                                                                    \
        fi

