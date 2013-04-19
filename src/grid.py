#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
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

import sys
from Xlib import X, display
import pygtk
import threading
import gobject
import gtk
import cairo
import math
from gtk import gdk
from gettext import gettext as _
import reporter

reporter = reporter.Reporter.get_instance()


# Grid; it show a nubered grid; is usefull to move the pointer in a selected area.
class Grid( threading.Thread ):


  def __init__(self):
    gtk.gdk.threads_init()
    
    self.display = gtk.gdk.display_get_default()
    self.screen = self.display.get_default_screen()
    self.screen_width = self.screen.get_width()
    self.screen_height = self.screen.get_height()
    
    self.win = gtk.Window(gtk.WINDOW_POPUP)
    self.size_x = self.screen_width
    self.size_y = self.screen_height
    self.position_x = 0
    self.position_y = 0

    self.win.set_app_paintable(True)
    self.win.set_decorated(False)
    self.win.set_skip_taskbar_hint(True)
    self.win.set_accept_focus(True)
    self.win.set_focus_on_map(True)
    self.win.set_deletable(False)
  
    self.win.set_usize ( self.screen_width, self.screen_height);
  
    self.win.set_keep_above(True)
    
    # Make the widget aware of the signal to catch.
    self.win.set_events(gtk.gdk.KEY_PRESS_MASK)
    
    # Connect the callback on_key_press to the signal key_press.
    self.win.connect("key_press_event", self.on_key_press)
    self.win.connect("delete-event", gtk.main_quit)
    self.win.connect("expose-event", self.expose)
    self.win.connect("screen-changed", self.screen_changed)

    self.win.add_events(gdk.BUTTON_PRESS_MASK)
    self.win.connect('button-press-event', self.clicked)
  
    self.screen_changed(self.win)
    threading.Thread.__init__ ( self )


  def screen_changed(self, widget, old_screen = None):
    # To check if the display supports alpha channels, get the colormap
    screen = widget.get_screen()
    colormap = screen.get_rgba_colormap()
    if colormap == None:
      noalpha = _("Your screen does not support alpha channels")
      reporter.report_failure(noalpha + ".")
      exit()
  
    # Now we have a colormap appropriate for the screen, use it
    widget.set_colormap(colormap)
  
    return False
  
    
  def run(self):
    gtk.gdk.threads_enter()
     
    self.win.show_all()
    self.win.fullscreen()
    
    gtk.main()
    
    gtk.gdk.threads_leave() 
        
         
  def put_label(self, cr, i, j):
    letter_x=self.size_x/6
    letter_y=self.size_y/6
    delta_x= self.position_x + ((i *2 + 1) * self.size_x)/6
    delta_y= self.position_y + ((j *2 + 1) * self.size_y)/6
    cr.set_source_rgba(1, 0, 0, 0.5)
    cr.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    font_size = math.sqrt(pow(letter_x, 2) + pow(letter_y, 2))
    cr.set_font_size(font_size)
    
    text = str(i+1 +(j*3))
    x_bearing, y_bearing, width, height = cr.text_extents(text)[:4]
    cr.move_to(delta_x - x_bearing - width / 2, delta_y - y_bearing - height / 2)
    cr.show_text(text)
    cr.stroke()  


  def show_grid(self, cr):
    cr.set_line_width(2)
    grid_cell = 2
    delta_x = 0
    delta_y = 0
    size_cell_x = self.size_x/3
    size_cell_y = self.size_y/3
    j = 0
    for i in range(grid_cell+1):
      delta_x=0
      for j in range(grid_cell+1):
        cr.set_source_rgba(1, 0, 0, 0.4)
        cr.rectangle(self.position_x + delta_x, self.position_y + delta_y, size_cell_x, size_cell_y)
        cr.stroke()  
        delta_x = delta_x + size_cell_x
        self.put_label(cr, i, j);
      delta_y = delta_y + size_cell_y
  
    
  def expose(self, widget, event):
    cr = widget.window.cairo_create()
    cr.set_source_rgba(0.0, 0.0, 0.0, 0)
    cr.set_operator(cairo.OPERATOR_SOURCE)
    cr.paint()
    self.show_grid(cr)
    pm = gtk.gdk.Pixmap(None, self.screen_width, self.screen_height, 1)
    pmcr = pm.cairo_create()
    pmcr.set_operator(cairo.OPERATOR_CLEAR);
    pmcr.paint()
    self.win.input_shape_combine_mask(pm, 0, 0)
    gtk.gdk.keyboard_grab(self.win.get_window())
    return False


  def select_cell(self,keyname):
    
    try:
      keyn = int(keyname)- 1
    except ValueError:
      no_valid_number = _("It is not a valid number")
      retry = _("Try again")
      reporter.report_failure(no_valid_number + "." + retry + ".")
      return
      
    if (keyn==-1):
      keyn=0
      
    self.win.hide()  
    keyl = keyn/3
    keyr = keyn%3
    self.position_y = self.position_y + keyl * self.size_y/3
    self.position_x = self.position_x + keyr *self.size_x/3
    self.size_x = self.size_x/3
    self.size_y = self.size_y/3
    d = display.Display()
    s = d.screen()
    root = s.root
    root.warp_pointer(self.position_x + self.size_x/2, self.position_y + self.size_y/2)
    d.sync()
    self.win.show_all()
    self.win.fullscreen()


  def on_key_press(self, widget, event):
    keyname = gtk.gdk.keyval_name(event.keyval)    
    self.select_cell(keyname)  


  def clicked(self, widget, event):
    gtk.main_quit()


  def stop(self):
    self.win.destroy()


