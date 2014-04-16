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

import alsaaudio
import wave
import simplejson as json
import subprocess
import os
import atexit
import urllib2
import statusicon

import ProcessText
import audioop
import math
import time
import gtk
import gettext
import locale
import logging
import reporter

from datetime import datetime
from gettext import gettext as _ 


APP_NAME='vox-launcher'

CHUNK     =  1024
CHANNELS  =     1
RATE      = 16000
MAXRESULT =     6

WAVE_OUTPUT_FILENAME = '/tmp/' + APP_NAME + '-recording.wav'
FLAC_OUTPUT_FILENAME = '/tmp/' + APP_NAME + '-recording.flac'

status_icon = statusicon.StatusIcon()
text_processor = ProcessText.ProcessText()
reporter = reporter.Reporter.get_instance()


# Clean the tool at exit.
def clean_up():
  try:
    os.remove(FLAC_OUTPUT_FILENAME)
  except OSError:
    pass
  
  text_processor.stop()
  reporter.quit()
  

# Send the audio file and get the receive.
def send_recv():
  audio = open(FLAC_OUTPUT_FILENAME, 'rb').read()
  filesize = os.path.getsize(FLAC_OUTPUT_FILENAME)
  
  HTTP_ADDRESS = 'http://www.google.com/speech-api/v1/recognize?lang=' + status_icon.get_language() + '&maxresults=' + str(MAXRESULT)
          
  req = urllib2.Request(url=HTTP_ADDRESS)
  req.add_header('Content-type','audio/x-flac; rate=16000')
  req.add_header('Content-length', str(filesize))
  req.add_data(audio)

  try:
    response = urllib2.urlopen(req)
    return response.read()
    
  except urllib2.HTTPError, e:
    error_message = e.read()
    logging.debug(error_message.lower().split('<title>')[1].split('</title>')[0])
    no_connection=_("Can't establish a connection to the server")
    reporter.report_failure(no_connection + ".")
  except urllib2.URLError, e:
    error_message = e.reason
    logging.debug(error_message)
    no_connection=_("Can't establish a connection to the server")
    reporter.report_failure(no_connection + ".")
   
  return None


def get_current_volume(data):
  LO        =  2000
  HI        = 32000
  log_lo = math.log(LO)
  log_hi = math.log(HI)
  
  # transform data to logarithmic scale
  try:
    peak = audioop.max(data, 2)
  except:
    return -1
       
  vu = (math.log(float(max(peak,1)))-log_lo)/(log_hi-log_lo)
    
  # transform the scale in the range 0...10
  current_volume = min(max((vu*10),0),10)
  return current_volume
    

# Capture audio input.
def capture_audio(inp):
  sound = []
  
  chunk = 0
  volume = 0
  volume_threshold = 1
  silence_threshold = 24
  silence_counter = 0
  
  status_icon.change_status(True)

  while(not status_icon.is_paused()):

    l, data = inp.read()
    
    if (not l or len(data)==0):
      continue
    
    current_volume = get_current_volume(data)
    
    if current_volume == -1:
       continue
       
    if chunk == 0:
       if current_volume < volume_threshold:
         if current_volume != 0:
           logging.debug( "Dropped package with volume " + str(current_volume) )
         continue
     
    else:
      if chunk>0 and volume == 0:
        silence_counter = silence_counter + 1
      else:
        silence_counter = 0
    
    if (silence_counter >= silence_threshold):
      logging.debug( "Detected " + str(silence_threshold) + " silent loop" )
      for i in range(1, silence_threshold):
        sound.pop()
      break 
      
    volume = current_volume

    status_icon.change_status(False)
    chunk = chunk + 1
    sound.append(data)
    time.sleep (RATE / CHUNK / 1000.0);

  if status_icon.is_paused():
    status_icon.change_status(False)
  
  logging.debug( "Recorded " + str(chunk) + "\n" )
  
  if (chunk > 16):
    return ''.join(sound)
  else:
    logging.debug( "Audio package dropped" )
    return ""


# Write the data in a wav file.
def write_wav(data):
  ''' Write string of data to WAV file of specified name '''
  wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(2)
  wf.setframerate(RATE)
  wf.writeframes(data)
  wf.close()


# Set up mic, capture audio, and return string of the result.
def setup_mic():
  inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL)
  inp.setchannels(CHANNELS)
  inp.setrate(RATE)
  inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
  inp.setperiodsize(CHUNK)
  return inp
  

# Handle the response.
def handle_response(resp):
  if resp =="":
    reporter.report_failure("Unrecognized command")
  else:
    try:
      hypotheses = json.loads(resp)['hypotheses']
    except json.decoder.JSONDecodeError:
      no_response=_("No response received")
      behind_firewall=_("Are you behind a firewall?")
      reporter.report_error(no_response + "." + behind_firewall)
      return     
      
    for index in range(len(hypotheses)):
      values = hypotheses[index].values()
          
      if len(values)==1:
        text = values[0]
        logging.debug( "Result \"" + text + "\" with unknown confidence" )
      else:
        confidence, text = values
        logging.debug( "Result \"" + text + "\" with confidence " + str(confidence) )
      
      retp = text_processor.process_text(text, status_icon.get_language())
          
      if (retp==True):
        return;


# Main.
def main():
  # Setup microphone
  inp = setup_mic()
    
  while (1):
    if status_icon.is_paused():
      continue;
      
    ''' Run through process of getting, converting, sending/receiving, and 
      processing data '''
  
    tstart = datetime.now()

    # code to speed test

    tend = datetime.now()
    logging.debug( "Init data capture " + str(tend - tstart) )
  
    # Capture an audio chunk
    data = capture_audio(inp)
    
    tend = datetime.now()
    logging.debug( "Finish data capture " + str(tend - tstart) )
    
    if data != "":
      # write to WAV file
      write_wav(data)
   
      tend = datetime.now()
      logging.debug( "Finish print wav " + str(tend - tstart) )
  
      subprocess.call(['sox', WAVE_OUTPUT_FILENAME, FLAC_OUTPUT_FILENAME, "rate", "16k", "pad", "0.5", "0.5"])
  
      tend = datetime.now()
      logging.debug( "Finish flac reencoding " + str(tend - tstart) )
      
      reporter.report_start_recognition()
      
      # Send and receive translation
      resp = send_recv()
      
      reporter.report_stop_recognition()  
      
      if resp != None: 
        tend = datetime.now()
        logging.debug( "Get google response " + str(tend - tstart) )
        handle_response(resp)
      
      
# Init locale.            
def init_localization():
  LOCALE_DOMAIN = APP_NAME
  gettext.textdomain(LOCALE_DOMAIN)
  gettext.install(LOCALE_DOMAIN)

# Init library to pass throgh system proxy.            
def init_proxy():
  proxy_support = urllib2.ProxyHandler({})
  opener = urllib2.build_opener(proxy_support)
  urllib2.install_opener(opener)    
                       
if __name__ == '__main__':
  init_localization()
  init_proxy()
  logging.basicConfig(level=logging.DEBUG)
  status_icon.start()
  atexit.register(clean_up)
  main()
  
