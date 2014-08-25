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

class LedArray:
  def __init__(self, red_pin, green_pin, blue_pin):
    self.red_pin = red_pin
    self.green_pin = green_pin
    self.blue_pin = blue_pin
    logging.info('initializing LEDs')
    PWM.start(self.red_pin, 0)
    PWM.start(self.green_pin, 0)
    PWM.start(self.blue_pin, 0)
    self.red_val = 0
    self.green_val = 0
    self.blue_val = 0
    self.leds_off()

  def led_state(self, pin, value, delay = 0):
    logging.debug('Setting LED %s to %d for %f s', pin, value, delay)
    if pin is self.red_pin:
      self.red_val = value
    elif pin is self.green_pin:
      self.green_val = value
    elif pin is self.blue_pin:
      self.blue_val = value
    logging.debug('Red = %d | Green = %d | Blue = %d', self.red_val,
                  self.green_val, self.blue_val)
    PWM.set_duty_cycle(pin, value)
    time.sleep(delay)

  def leds_off(self):
    self.led_state(self.red_pin, 0)
    self.led_state(self.green_pin, 0)
    self.led_state(self.blue_pin, 0)

  def loop(self, rate):
    # fade from blue to violet
    for r in range(1, 100):
      self.led_state(self.red_pin, r, rate)
    # fade from violet to red
    for b in range(100, 1, -1):
      self.led_state(self.blue_pin, b, rate)
    # fade from red to yellow
    for g in range(1, 100):
      self.led_state(self.green_pin, g, rate)
    # fade from yellow to green
    for r in range(100, 1, -1):
      self.led_state(self.red_pin, r, rate)
    # fade from green to teal
    for b in range(1, 100):
      self.led_state(self.blue_pin, b, rate)
    # fade from teal to blue
    for g in range(100, 1, -1):
      self.led_state(self.green_pin, g, rate)

  def test_colors(self, delay = 3):
    logging.info('red full for %d s, half for %d s' % (delay, delay))
    self.leds_off()
    self.led_state(self.red_pin, 100, delay)
    self.led_state(self.red_pin, 50, delay)
    logging.info('green full for %d s, half for %d s' % (delay, delay))
    self.leds_off()
    self.led_state(self.green_pin, 100, delay)
    self.led_state(self.red_pin, 50, delay)
    logging.info('blue full for %d s, half for %d s' % (delay, delay))
    self.leds_off()
    self.led_state(self.blue_pin, 100, delay)
    self.led_state(self.red_pin, 50, delay)
    logging.info('all on (white) full for %d s' % delay)
    self.leds_off()
    self.led_state(self.red_pin, 100)
    self.led_state(self.green_pin, 100)
    self.led_state(self.blue_pin, 100, delay)
    logging.info('test complete')

  def __exit__(self):
    PWM.stop(self.red_pin)
    PWM.stop(self.green_pin)
    PWM.stop(self.blue_pin)
    PWM.cleanup()
    logging.info('cleanup complete')

def main():
  parser = argparse.ArgumentParser(description='LED control script')
  parser.add_argument('-v', '--verbose', action='count')
  parser.add_argument('-t', '--test', action='store_true')
  parser.add_argument('-r', '--rate', default=0.05, type=float)
  args = parser.parse_args()
  logging.basicConfig(format='%(levelname)s:%(message)s', 
                      level=logging.WARNING - 10 * (args.verbose or 0))

  led_array = LedArray(REDPIN, GREENPIN, BLUEPIN)
  atexit.register(led_array.__exit__)

  if args.test:
    led_array.test_colors()
  else:
   while(1):
     led_array.loop(args.rate)

main()
