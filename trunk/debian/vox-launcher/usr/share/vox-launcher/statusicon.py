#!/usr/bin/python
#
# ProcessText.py
# Copyright (C) Pilolli 2012 <pilolli.pietro@gmail.com>
# 
# vox-launcher is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# vox-launcher is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import threading
import os
import gettext
                   
class StatusIcon( threading.Thread ):
           
    def change_status(self,ready):
        if (ready):
            self.statusicon.set_from_file("icons/green.png")
        else:
            self.statusicon.set_from_file("icons/red.png")
             
    def __init__(self):
        gtk.gdk.threads_init()
        # Supported Google speech api languages
        self.supported_langs = ["de-DE", "en-GB", "en-US", "es-ES", "fr-FR", "it-IT"]
        self.lang=os.environ['LANG'].split(".")[0].replace("_","-")
        self.paused = False
        self.statusicon = gtk.StatusIcon()
        threading.Thread.__init__ ( self )  
		
    def run(self):
        self.statusicon.set_from_file("green.png")
        self.statusicon.connect("button-press-event", self.button_press)
        self.statusicon.set_visible(True)
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()    
    
    def quit(self,widget):
        gtk.main_quit()
        exit()
    
    def onPause(self, widget, data=None):
        if (self.paused):
            self.paused = False
        else:
            self.paused = True
    
    # action on language submenu items
    def onLang(self, widget, lng):
        self.lang = lng
    
    def get_language(self):
        return self.lang
    
    def is_paused(self):
        return self.paused
    
    # activate callback
    def button_press(self, widget, event):
        menu = gtk.Menu()

        # Pause item menu
        if (self.paused):
            rmItem = gtk.ImageMenuItem(gtk.STOCK_EXECUTE)
        else:
            rmItem = gtk.ImageMenuItem(gtk.STOCK_MEDIA_STOP)
        rmItem.connect('activate', self.onPause)
        rmItem.show()
        menu.append(rmItem)
        
        # Preference item menu
        rmItem = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        rmItem.show()
        # Creating and linking langues submenu
        menulngs = gtk.Menu()
        rmItem.set_submenu(menulngs)
        
        # Creating languages items in submenu
        # one empty item to initiate radioitem group
        smItem = gtk.RadioMenuItem(None, None)
        for i in self.supported_langs:
            # Creating new item
            smItem = gtk.RadioMenuItem(smItem, i, True)
            # ... adding item in submenu
            menulngs.append(smItem)
            # linking it with onLang fonction
            smItem.connect("toggled", self.onLang, i)
            # i is defaut language activating radio button
            if i == self.lang :
                smItem.set_active(True)
            # show item
            smItem.show()
        
        menu.append(rmItem)
        
        about = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about.connect("activate", self.show_about_dialog)
        about.show()
        
        quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit.connect("activate", self.quit)
        quit.show()
        
        menu.append(about)
        menu.append(quit)
        menu.show_all()
        
        menu.popup(None, None, gtk.status_icon_position_menu, event.button, event.time, self.statusicon)
      
        
    def show_about_dialog(self, widget):
		about_dialog = gtk.AboutDialog()
		
		about_dialog.set_destroy_with_parent(True)
		about_dialog.set_name("Vox launcher")
		about_dialog.set_version("1.0")
		about_dialog.set_authors(["Pietro Pilolli"])
		
		about_dialog.run()
		about_dialog.destroy()






