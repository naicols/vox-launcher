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

class Reporter():

  def __init__(self):
     pynotify.init("vox-launcher")
    
  def acoustic_report_failure(self):
    command = 'aplay ' + error_sound
    args = shlex.split(command)
    process = subprocess.Popen(args)
    
  def acoustic_report_success(self):
    command = 'aplay ' + info_sound
    args = shlex.split(command)
    process = subprocess.Popen(args)
        
  def report_start_recognition(self):
    command = 'vox-osd --splash icons/throbber.gif "Performing Recognition"'
    args = shlex.split(command)
    process = subprocess.Popen(args)
    return process


  def report_stop_recognition(self, process):
    if (process != None):
       process.kill()


  def report_failure(self, msg):
    self.acoustic_report_failure()
    n = pynotify.Notification("Error", msg, 'dialog-error')
    n.set_timeout(1000)
    n.show()
    
    
  def report_success(self, msg):
    self.acoustic_report_success()
    n = pynotify.Notification("Info", "Done",'dialog-information')
    n.set_timeout(1000)
    n.show()

