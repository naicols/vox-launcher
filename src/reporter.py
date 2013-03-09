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

import pynotify
import shlex, subprocess

sound_folder="/usr/share/sounds/"
info_sound= sound_folder + "info.wav"
error_sound= sound_folder + "error.wav"

# Class with some usefull methods to report status of the tool to the user.
class Reporter():


  n = pynotify.Notification("Info", "Started",'dialog-information')
  process = None


  def __init__(self):
     pynotify.init("vox-launcher")
     self.n.set_timeout(1000)
     
  
  def acoustic_report_failure(self):
    command = 'aplay ' + error_sound
    args = shlex.split(command)
    subprocess.Popen(args)

    
  def acoustic_report_success(self):
    command = 'aplay ' + info_sound
    args = shlex.split(command)
    subprocess.Popen(args)

        
  def report_start_recognition(self):
    command = 'vox-osd --splash icons/throbber.gif "Performing Recognition"'
    args = shlex.split(command)
    self.process = subprocess.Popen(args)
    

  def report_stop_recognition(self):
    if (self.process != None):
       self.process.kill()


  def report_failure(self, msg):
    self.acoustic_report_failure()
    self.n.update("Error", msg, 'dialog-error')
    self.n.show()
    
    
  def report_success(self, msg):
    self.acoustic_report_success()
    self.n.update("Info", "Done",'dialog-information')
    self.n.show()
    
  def quit(self):
    self.report_stop_recognition()
    self.n.close()


