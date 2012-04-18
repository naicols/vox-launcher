## Process this file with automake to produce Makefile.in

EXTRA_DIST = \
	vox-launcher.desktop.in   

desktopdir = $(prefix)/share/applications
desktop_in_files = vox-launcher.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
uiiconsdir=$(prefix)/share/vox-launcher

@INTLTOOL_DESKTOP_RULE@

pixmapdir = $(prefix)/share/icons
pixmap_DATA = icons/vox-launcher.png


install-data-local:
	cp -r icons $(DESTDIR)$(uiiconsdir)
	mkdir -p $(DESTDIR)$(prefix)/share/pixmaps
	cp $(pixmap_DATA) $(DESTDIR)$(prefix)/share/pixmaps

	@if test x"$(XDG_UTILS)" != x; then                                                                                                          \
		echo "Register iwb mimetype";                                                                                                        \
		xdg-desktop-menu install --mode user --novendor vox-launcher.desktop;                                                                     \
	fi

# Remove ui directory on uninstall
uninstall-local:
	rm -fr $(uiiconsdir) 
