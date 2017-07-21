#!/usr/bin/env python

#
#      Copyright (C) 2015-2017 Jozef Hutting <jehutting@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
import subprocess
import logging
import threading
import time
import thread
import termios
import tty
from random import randint
from omxplayer.player import OMXPlayer
from omxplayer.player import logger
import RPi.GPIO as GPIO

__author__ = 'Jozef Hutting'
__copyright__ = 'Copyright (C) 2015 Jozef Hutting <jehutting@gmail.com>'
__license__ = 'GPLv2'
__version__ = '0.14'

# USAGE
#     sudo python omxplayer-pir FILE DURATION
# where
#     FILE is the name of the file to play 


# REAL OMXPLAYER options
OMXPLAYER_ARGS = [
     #'--display=4',  # Raspberry Pi touchscreen
     '--no-osd', # Do not display status information on screen
     #'--loop', # Loop file.
     #'-b',
     '--aspect-mode', #full screen
     'stretch',
     #'--aidx',
     #'-1',
     '--hw'
    ]

#omxplayer wrapper variable
omxplayer = None

class PirControl():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.gpio = 14
        GPIO.setup(self.gpio, GPIO.IN)
        self.state = self.__get_state()
        
    def __get_state(self):
        return GPIO.input(self.gpio)

    def start(self):
        GPIO.add_event_detect(self.gpio, GPIO.BOTH, callback=self.edge_callback)
        self.state = self.__get_state()

    def edge_callback(self, channel):
        global omxplayer
        state = self.__get_state()

        if state != self.state:
            if state == 1:
                print 'Motion detected!'
                omxplayer.play()
            else:
                print 'NO motion detected!'
            self.state = state

    def motion_detected(self):
        self.state = self.__get_state()
        return self.state == 1

class Main():

    def run(self, filename):
      global omxplayer

      pir_control = PirControl()
      return_code = 0 # OK

      try:    

          while(pir_control.motion_detected()):
              continue;
          
          omxplayer = OMXPlayer(filename, OMXPLAYER_ARGS, None, None, True)
          omxplayer.pause()

          print 'Video player is armed!'
          print str(omxplayer.duration())

          pir_control.start()
          
          i = duration
          
          while True:
              status = 0
              
              while status != 1:
                  pos = omxplayer.position()
                  #print str(pos)
                  if pos >= i:    
                      status = 1
                  continue
              if pir_control.motion_detected() == 0:
                  omxplayer.pause()

              i += duration
              if i >= omxplayer.duration() - duration:
                  i = duration
                  omxplayer.set_position(0)
                  
              #print "i="+str(i)

      except IOError as e:
          return_code = -1

      except KeyboardInterrupt:
          print 'KeyboardInterrupt'
          omxplayer.quit()

      print('EXIT')
      GPIO.cleanup()
      return return_code


if __name__ == '__main__':

    logger.propagate = False

    # we need at least one FILE argument...
    if len(sys.argv) < 3:
        print('Error: missing FILE and duration argument!')
        sys.exit(-3)

    # ... and at most one FILE argument
    if len(sys.argv) > 3:
        print('Error: too many arguments! Only one FILE argument expected.')
        sys.exit(-2)

    # so we only have one argument and that's the FILE argument
    filename = sys.argv[1]
    duration = int(sys.argv[2])

    # check if the file exists
    if not os.path.isfile(filename):
        print('Error: File "{0}" not found!'.format(filename))
        sys.exit(-1)
  
    # so far so good, so let's play :-)
    try:
        mainloop = Main();
        return_code = mainloop.run(filename);
    
    finally:
        pass
       
    sys.exit(return_code);
