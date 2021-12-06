#! /usr/bin/python
# LED clock control script for BeagleBone Black.
# This assumes a tri color LED array is connected to
# three PWM signals on the bone.

import argparse
import atexit
import led_array
import logging
import sys
import time

class ColorClock:
  """Determine a color for a particular time of day."""
  def __init__(self):
    self.now = time.localtime()
    self.r = 0
    self.g = 0
    self.b = 0

  def current_color(self):
    self.now = time.localtime()
    logging.info(time.strftime("%a, %d %b %Y %H:%M:%S +0000", self.now))
    self.select_rgb(self.now.tm_min)

  def select_rgb(self, tm_val):
    assert 0 <= tm_val <= 59, 'not a minute or second value'
    if tm_val <= 20:
      self.r = 100 - tm_val * 5
      self.g = tm_val * 5
      self.b = 0
    elif tm_val <= 40:
      self.r = 0
      self.g = 100 - ((tm_val - 20) * 5)
      self.b = (tm_val - 20) * 5
    else:
      self.r = (tm_val - 40) * 5
      self.g = 0
      self.b = 100 - ((tm_val - 40) * 5)

def main():
  parser = argparse.ArgumentParser(description='LED control script',
             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-v', '--verbose', action='count')
  parser.add_argument('-t', '--test', action='store_true',
                      help='Run a basic test sequence.')
  parser.add_argument('--warningpulse', action='store_true',
                      help='Pulse on 30 minute boundaries.')
  parser.add_argument('--red_pin_name', default="P8_13", type=str,
                      help='Name of the red PWM pin.')
  parser.add_argument('--green_pin_name', default="P8_19", type=str,
                      help='Name of the green PWM pin.')
  parser.add_argument('--blue_pin_name', default="P9_14", type=str,
                      help='Name of the blue PWM pin.')
  parser.add_argument('--pwm_max_value', default=100, type=int,
                      help='Max value the PWM driver will accept.')
  args = parser.parse_args()
  logging.basicConfig(format='%(levelname)s:%(message)s', 
                      level=logging.WARNING - 10 * (args.verbose or 0))

  array = led_array.LedArray(args.red_pin_name, args.green_pin_name,
                                 args.blue_pin_name, args.pwm_max_value)
  atexit.register(array.__exit__)
  color_clock = ColorClock()

  if args.test:
    array.test_colors(args.rate)
    sys.exit()
  while(1):
    minute = time.localtime().tm_min
    hour = time.localtime().tm_hour
    if args.warningpulse and minute in [29, 59]:
      # Pulse red 10 times on 30 minute boundaries.
      array.pulse(100, 0, 0, 3.0, 10)
      # Pulse blue the hour on the hour.
      if minute == 59:
        array.pulse(0, 0, 100, 3.0, hour + 1)
    else:
      color_clock.current_color()
      array.fade(color_clock.r, color_clock.g, color_clock.b, 30.0)
   
main()
