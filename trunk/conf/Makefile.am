## Process this file with automake to produce Makefile.in

etcdir = /etc/vox-launcher

@INTLTOOL_DESKTOP_RULE@


install-data-local:
	mkdir -p $(DESTDIR)$(etcdir) 
	cp -r *.conf $(DESTDIR)$(etcdir) 

# Remove ui directory on uninstall
uninstall-local:
	rm -fr $(etcdir) 

