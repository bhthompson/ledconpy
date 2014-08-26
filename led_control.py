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

  def fade(self, r, g, b, rate):
    red_start = self.red_val
    green_start = self.green_val
    blue_start = self.blue_val
    logging.info('fade from: Red = %d | Green = %d | Blue = %d',
                 red_start, green_start, blue_start)
    logging.info('fade to  : Red = %d | Green = %d | Blue = %d', r, g, b)
    for step in range(1, 101):
      r_step = (r * step)/100 + (red_start * abs(step - 100))/100
      g_step = (g * step)/100 + (green_start * abs(step - 100))/100
      b_step = (b * step)/100 + (blue_start * abs(step - 100))/100
      self.led_state(self.red_pin, r_step)
      self.led_state(self.green_pin, g_step)
      self.led_state(self.blue_pin, b_step)
      time.sleep(rate / 100)

  def leds_off(self):
    self.led_state(self.red_pin, 0)
    self.led_state(self.green_pin, 0)
    self.led_state(self.blue_pin, 0)

  def led_state(self, pin, value, delay = 0):
    logging.debug('Setting LED %s to %d for %f s', pin, value, delay)
    if pin is self.red_pin:
      self.red_val = value
    elif pin is self.green_pin:
      self.green_val = value
    elif pin is self.blue_pin:
      self.blue_val = value
    else:
      logging.warning('Invalid pin given to led_state')
    logging.debug('Red = %d | Green = %d | Blue = %d', self.red_val,
                  self.green_val, self.blue_val)
    PWM.set_duty_cycle(pin, value)
    time.sleep(delay)

  def loop(self, rate):
    # fade from blue to violet
    self.fade(100, 0, 100, rate)
    # fade from violet to red
    self.fade(100, 0, 0, rate)
    # fade from red to yellow
    self.fade(100, 100, 0, rate)
    # fade from yellow to green
    self.fade(0, 100, 0, rate)
    # fade from green to teal
    self.fade(0, 100, 100, rate)
    # fade from teal to blue
    self.fade(0, 0, 100, rate)

  def test_colors(self, delay = 1):
    logging.info('red full for %f s, half for %f s' % (delay, delay))
    self.leds_off()
    self.led_state(self.red_pin, 100, delay)
    self.led_state(self.red_pin, 50, delay)
    logging.info('green full for %f s, half for %f s' % (delay, delay))
    self.leds_off()
    self.led_state(self.green_pin, 100, delay)
    self.led_state(self.red_pin, 50, delay)
    logging.info('blue full for %f s, half for %f s' % (delay, delay))
    self.leds_off()
    self.led_state(self.blue_pin, 100, delay)
    self.led_state(self.red_pin, 50, delay)
    logging.info('all on (white) full for %f s' % delay)
    self.leds_off()
    self.led_state(self.red_pin, 100)
    self.led_state(self.green_pin, 100)
    self.led_state(self.blue_pin, 100, delay)
    logging.info('fade to off in %f s' % delay)
    self.fade(0, 0, 0, delay)
    logging.info('fade to red in %f s' % delay)
    self.fade(100, 0, 0, delay)
    logging.info('fade to purple in %f s' % delay)
    self.fade(100, 0, 100, delay)
    logging.info('fade to white in %f s' % delay)
    self.fade(100, 100, 100, delay)
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
  parser.add_argument('-t', '--test', action='store_true',
                      help='Run a basic test sequence.')
  parser.add_argument('-r', '--rate', default=1.0, type=float,
                      help='Approximate rate in seconds for transitions.')
  args = parser.parse_args()
  logging.basicConfig(format='%(levelname)s:%(message)s', 
                      level=logging.WARNING - 10 * (args.verbose or 0))

  led_array = LedArray(REDPIN, GREENPIN, BLUEPIN)
  atexit.register(led_array.__exit__)

  if args.test:
    led_array.test_colors(args.rate)
  else:
   while(1):
     led_array.loop(args.rate)

main()
