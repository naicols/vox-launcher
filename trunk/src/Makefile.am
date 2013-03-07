## Process this file with automake to produce Makefile.in
## Created by Anjuta



## The main script
bin_SCRIPTS = vox-launcher vox-osd

## Directory where .class files will be installed
vox_launcherdir = $(prefix)/share/vox-launcher


vox_launcher_PYTHON =   \
	vox-launcher.py \
	grid.py         \
	ProcessText.py  \
	reporter.py     \
	sparql.py       \
	statusicon.py



# Remove ui directory on uninstall
uninstall-local:

	-rm -r $(datadir)/vox-launcher
