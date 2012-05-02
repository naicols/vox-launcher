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

import os
import time
import subprocess
import pynotify
import logging
import grid



class ProcessText():

    def __init__(self):
        self.is_grid_running = False
        self.grid = grid.Grid() 

    def insert_text(self, t, lang):
        command =  "xte \"str " + t + "\""    
        os.system(command)

    def program_exists(self, fname):
        for p in os.environ['PATH'].split(os.pathsep):
            if os.path.isfile(os.path.join(p, fname)):
                return True
        return False

    def get_matching_command(self, t, lang, prefix):
        fileName = '/etc/vox-launcher/vox-launcher_' + lang + '.conf'
        if not os.path.isfile(fileName):
            return ""
        
        file = open(fileName,"r")
        ln = 0
    
        for line in file:
            ln = ln + 1
            if line.startswith('#') or line.isspace():
                continue
            else:
                temp=line.split("->")
                if len(temp) == 2:
                    exp = temp[0].strip()
                    if t == exp:
                        command = temp[1].strip()
                        n = pynotify.Notification("Info", prefix + " " + exp, icon='vox-launcher')
                        n.set_urgency(pynotify.URGENCY_CRITICAL)
                        n.set_timeout(1000)
                        n.show()
                        file.close()
                        return command
                else:
                    logging.debug( "can't parse line " + str(ln) )

        file.close()
        return ""

    def open_program(self, t, lang, prefix):
        command = t

        new_command = self.get_matching_command(t, lang, prefix)
        if new_command!="":
            command = new_command
        
        logging.debug( "Command " + command )
        progname = command.split(" ")[0]
        if self.program_exists(progname):
            subprocess.Popen(command, shell=True)
            return True
        
        return False
            
    def process_text(self, values, lang):
        ''' Take in a tuple of the confidence and result and do the appropriate 
            action or also the text'''

        if len(values)==1:
            text = values[0]
            logging.debug( "Result \"" + text + "\" with unknown confidence" )
        else:
            confidence, text = values
            logging.debug( "Result \"" + text + "\" with confidence " + str(confidence) )

        if len(text)==1:
            if self.is_grid_running == True:
                if '0' <= text[:1] <= '9':
                    #send command to grid
                    self.grid.select_cell(text)
                    return True;
            else:
                self.insert_text(text, lang)
                return True
    
        if text == "grid" or text == "griglia":
            if self.grid!=None and self.is_grid_running == True:
               self.grid.stop()
            if (self.grid == None):
                self.grid = grid.Grid()
            self.grid.start()
            self.is_grid_running = True
            return True
                
        # Ignore some token in initial position
        if text.startswith('open') or text.startswith('run') or text.startswith('apri'):
            startpos = text.find(" ") + 1
            t = text[startpos:]
            return self.open_program(t, lang, text.split(" ")[0].strip())
        # Keyword in order to write with vocal keyboard
        elif text.startswith('scrivi') or text.startswith('write'):
            startpos = text.find(" ") + 1
            t = text[startpos:]
            self.insert_text(t, lang)
            return True
        # Unsuccessful; display result
        else:
            status = self.open_program(text, lang, "")
            if self.is_grid_running == True and status == True:
                self.grid.stop()
                self.grid = None
                self.is_grid_running = False
            return status
