#! /usr/bin/python
# LED control script for BeagleBone Black.
# This assumes a tri color LED array is connected to
# three PWM signals on the bone.

import Adafruit_BBIO.PWM as PWM
import argparse
import atexit
import logging
import time

# Set these to the PWM pins being used.
REDPIN = "P8_13"
GREENPIN = "P8_19"
BLUEPIN = "P9_14"

FADESPEED = .05     # make this higher to slow down

def init_leds():
  logging.info('initializing LEDs')
  PWM.start(REDPIN, 100)
  PWM.start(GREENPIN, 100)
  PWM.start(BLUEPIN, 100)
  leds_off()

def led_state(pin, value, delay = 0):
  logging.debug('Setting LED %s to %d for %d', pin, value, delay)
  PWM.set_duty_cycle(pin, value)
  time.sleep(delay)

def leds_off():
  led_state(REDPIN, 0)
  led_state(GREENPIN, 0)
  led_state(BLUEPIN, 0)

def loop(rate):
  # fade from blue to violet
  for r in range(1, 100):
    led_state(REDPIN, r, rate)
  # fade from violet to red
  for b in range(100, 1, -1):
    led_state(BLUEPIN, b, rate)
  # fade from red to yellow
  for g in range(1, 100):
    led_state(GREENPIN, g, rate)
  # fade from yellow to green
  for r in range(100, 1, -1):
    led_state(REDPIN, r, rate)
  # fade from green to teal
  for b in range(1, 100):
    led_state(BLUEPIN, b, rate)
  # fade from teal to blue
  for g in range(100, 1, -1):
    led_state(GREENPIN, g, rate)

def test_colors(delay = 3):
  logging.info('red full for %d s, half for %d s' % (delay, delay))
  leds_off()
  led_state(REDPIN, 100, delay)
  led_state(REDPIN, 50, delay)
  logging.info('green full for %d s, half for %d s' % (delay, delay))
  leds_off()
  led_state(GREENPIN, 100, delay)
  led_state(REDPIN, 50, delay)
  logging.info('blue full for %d s, half for %d s' % (delay, delay))
  leds_off()
  led_state(BLUEPIN, 100, delay)
  led_state(REDPIN, 50, delay)
  logging.info('all on (white) full for %d s' % delay)
  leds_off()
  led_state(REDPIN, 100)
  led_state(GREENPIN, 100)
  led_state(BLUEPIN, 100, delay)
  logging.info('test complete')

def cleanup():
  PWM.stop(REDPIN)
  PWM.stop(GREENPIN)
  PWM.stop(BLUEPIN)
  PWM.cleanup()
  logging.info('cleanup complete')

def main():
  atexit.register(cleanup)
  parser = argparse.ArgumentParser(description='LED control script')
  parser.add_argument('-v', '--verbose', action='count')
  parser.add_argument('-t', '--test', action='store_true')
  parser.add_argument('-r', '--rate', default=0.05, type=float)
  args = parser.parse_args()
  logging.basicConfig(format='%(levelname)s:%(message)s', 
                      level=logging.WARNING - 10 * (args.verbose or 0))

  init_leds()
  if args.test:
    test_colors()
  else:
   while(1):
     loop(args.rate)
  cleanup()

main()
