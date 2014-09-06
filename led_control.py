#! /usr/bin/python
# LED control script for BeagleBone Black.
# This assumes a tri color LED array is connected to
# three PWM signals on the bone.

import argparse
import atexit
import led_array
import logging
import sys

def main():
  parser = argparse.ArgumentParser(description='LED control script',
             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-v', '--verbose', action='count')
  parser.add_argument('-t', '--test', action='store_true',
                      help='Run a basic test sequence.')
  parser.add_argument('-r', '--rate', default=1.0, type=float,
                      help='Approximate rate in seconds for transitions.')
  parser.add_argument('-f', '--filename', default=None, type=str,
                      help='File containing a LED sequence.')
  parser.add_argument('--random', action='store_true',
                      help='Change the LED colors randomly')
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



  if args.test:
    array.test_colors(args.rate)
    sys.exit()
  elif args.filename is not None:
    while(1):
      array.process_file(args.filename)
  elif args.random:
    while(1):
      array.random_color(args.rate, True)
  while(1):
    array.color_cycle(args.rate)
   
main()
