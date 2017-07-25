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

__author__ = 'Jozef Hutting, Rudy Nurhadi, Irvan Rahadian'
__copyright__ = 'Copyright (C) 2015 Jozef Hutting <jehutting@gmail.com>'
__license__ = 'GPLv2'
__version__ = '0.15'

# USAGE
#     sudo python automotion FILE DURATIONPERSECTION
# where
#     FILE is the name of the file to play 


# REAL OMXPLAYER options
OMXPLAYER_ARGS = [
     #'--display=4',  # Raspberry Pi touchscreen
     '--no-osd', # Do not display status information on screen
     #'--loop', # Loop file.
     #'-b', # Blank background
     '--aspect-mode', # Full screen
     'stretch',
     #'--aidx', # No Sound
     #'-1',
     '--hw'
    ]

#omxplayer wrapper variable
omxplayer = None

class GPIOControl():
	def __init__(self):
                self.laser_gpio = 14
                self.relay_gpio = 15
                
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.laser_gpio, GPIO.IN)
		GPIO.setup(self.relay_gpio, GPIO.OUT)
		self.state = self.__get_state()
		
	def __get_state(self):
		return GPIO.input(self.laser_gpio)

	def start(self):
		GPIO.add_event_detect(self.laser_gpio, GPIO.BOTH, callback=self.edge_callback)
		self.state = self.__get_state()

	def edge_callback(self, channel):
		global omxplayer
		state = self.__get_state()

		if state != self.state:
			if state == 1:
				print 'Motion detected!'
				GPIO.output(self.relay_gpio, GPIO.HIGH)
				time.sleep(0)
				omxplayer.play()
			else:
				print 'NO motion detected!'
			self.state = state

	def motion_detected(self):
		self.state = self.__get_state()
		return self.state == 1
		
	def turn_off_relay(self):
		GPIO.output(self.relay_gpio, GPIO.LOW)

class Main():
	def run(self, filename):
		global omxplayer

		gpio_control = GPIOControl()
		return_code = 0 # OK

		try:    
			omxplayer = OMXPlayer(filename, OMXPLAYER_ARGS, None, None, True)
			omxplayer.pause()
			
			print 'Video player is armed!'
			print 'Video duration = ' + str(omxplayer.duration())
			
			#while(gpio_control.motion_detected()):
			#	continue;
			
			gpio_control.start()
			
			#loop_num = int(omxplayer.duration() / duration_sect)
			
			i = duration_sect
			last_sect = False

			while True:
				status = 0

				while status != 1:
					pos = omxplayer.position()
					#print str(pos)
					if pos + 0.01 >= i:
                                                if last_sect: 
                                                        i = 0
                                                        omxplayer.set_position(0)
                                                status = 1
					continue
				if gpio_control.motion_detected() == 0:
					gpio_control.turn_off_relay()
					omxplayer.pause()

				i += duration_sect
				if i + duration_sect >= omxplayer.duration():
                                        last_sect = True

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

	# we need at least one FILE and duration argument...
	if len(sys.argv) < 3:
		print('Error: missing FILE and duration argument!')
		sys.exit(-3)

	# ... and at most one FILE and duration argument
	if len(sys.argv) > 3:
		print('Error: too many arguments! Only FILE and duration argument expected.')
		sys.exit(-2)

	# so we have two arguments and that's the FILE and duration argument
	filename = sys.argv[1]
	duration_sect = int(sys.argv[2])

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
