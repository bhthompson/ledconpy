#! /usr/bin/python
# LED control script for BeagleBone Black.
# This assumes a tri color LED array is connected to
# three PWM signals on the bone.

import Adafruit_BBIO.PWM as PWM
import argparse
import atexit
import logging
import random
import time

class LedArray:
  """Control interface for RGB LEDs. Requires the pin names
  to be used for the PWM channels and the max value the PWM driver
  will accept."""
  def __init__(self, red_pin, green_pin, blue_pin, pwm_max):
    self.red_pin = red_pin
    self.green_pin = green_pin
    self.blue_pin = blue_pin
    self.pwm_max = pwm_max
    logging.info('initializing LEDs')
    PWM.start(self.red_pin, 0)
    PWM.start(self.green_pin, 0)
    PWM.start(self.blue_pin, 0)
    self.red_val = 0
    self.green_val = 0
    self.blue_val = 0
    self.leds_off()

  def color_cycle(self, rate):
    """Smoothly cycle through colors."""
    # fade from blue to violet
    self.fade(self.pwm_max, 0, self.pwm_max, rate)
    # fade from violet to red
    self.fade(self.pwm_max, 0, 0, rate)
    # fade from red to yellow
    self.fade(self.pwm_max, self.pwm_max, 0, rate)
    # fade from yellow to green
    self.fade(0, self.pwm_max, 0, rate)
    # fade from green to teal
    self.fade(0, self.pwm_max, self.pwm_max, rate)
    # fade from teal to blue
    self.fade(0, 0, self.pwm_max, rate)
 
  def fade(self, r, g, b, rate):
    """Fade the LEDs from their current color to a new color.
    The rate value defines an approximate time to complete the fade.
    This is approximate as it assumes the actual calculations take 0 time,
    so on an infinitely fast processor it will be accurate, slower systems
    will take longer."""
    red_start = self.red_val
    green_start = self.green_val
    blue_start = self.blue_val
    logging.info('fade from: Red = %d | Green = %d | Blue = %d',
                 red_start, green_start, blue_start)
    logging.info('fade to  : Red = %d | Green = %d | Blue = %d', r, g, b)
    for step in range(1, self.pwm_max + 1):
      r_step = ((r * step)/self.pwm_max +
               (red_start * abs(step - self.pwm_max))/self.pwm_max)
      g_step = ((g * step)/self.pwm_max +
               (green_start * abs(step - self.pwm_max))/self.pwm_max)
      b_step = ((b * step)/self.pwm_max +
               (blue_start * abs(step - self.pwm_max))/self.pwm_max)
      self.led_state(self.red_pin, r_step)
      self.led_state(self.green_pin, g_step)
      self.led_state(self.blue_pin, b_step)
      time.sleep(rate / self.pwm_max)

  def leds_off(self):
    """Set all the LEDs to 0"""
    self.led_state(self.red_pin, 0)
    self.led_state(self.green_pin, 0)
    self.led_state(self.blue_pin, 0)

  def led_state(self, pin, value):
    """Set a LED to a specific value. Note that this just chanses one color
    on the LED array."""
    logging.debug('Setting LED %s to %d', pin, value)
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

  def random_color(self, rate = 0, fade = False):
    """Set the LEDs to a random color, smoothly if fade is set."""
    if fade:
      self.fade(random.randrange(self.pwm_max + 1),
                random.randrange(self.pwm_max + 1),
                random.randrange(self.pwm_max + 1), rate)
    else:
      self.led_state(self.red_pin, random.randrange(self.pwm_max + 1))
      self.led_state(self.green_pin, random.randrange(self.pwm_max + 1))
      self.led_state(self.blue_pin, random.randrange(self.pwm_max + 1))
      time.sleep(rate)

  def test_colors(self, delay = 1):
    """Test the color channels and PWM capability."""
    logging.info('red full for %f s, half for %f s' % (delay, delay))
    self.leds_off()
    self.led_state(self.red_pin, self.pwm_max)
    time.sleep(delay)
    self.led_state(self.red_pin, self.pwm_max/2)
    time.sleep(delay)
    logging.info('green full for %f s, half for %f s' % (delay, delay))
    self.leds_off()
    self.led_state(self.green_pin, self.pwm_max)
    time.sleep(delay)
    self.led_state(self.red_pin, self.pwm_max/2)
    time.sleep(delay)
    logging.info('blue full for %f s, half for %f s' % (delay, delay))
    self.leds_off()
    self.led_state(self.blue_pin, self.pwm_max)
    time.sleep(delay)
    self.led_state(self.red_pin, self.pwm_max/2)
    time.sleep(delay)
    logging.info('all on (white) full for %f s' % delay)
    self.leds_off()
    self.led_state(self.red_pin, self.pwm_max)
    self.led_state(self.green_pin, self.pwm_max)
    self.led_state(self.blue_pin, self.pwm_max)
    time.sleep(delay)
    logging.info('fade to off in %f s' % delay)
    self.fade(0, 0, 0, delay)
    logging.info('fade to red in %f s' % delay)
    self.fade(self.pwm_max, 0, 0, delay)
    logging.info('fade to purple in %f s' % delay)
    self.fade(self.pwm_max, 0, self.pwm_max, delay)
    logging.info('fade to white in %f s' % delay)
    self.fade(self.pwm_max, self.pwm_max, self.pwm_max, delay)
    logging.info('test complete')

  def __exit__(self):
    PWM.stop(self.red_pin)
    PWM.stop(self.green_pin)
    PWM.stop(self.blue_pin)
    PWM.cleanup()
    logging.info('cleanup complete')

def main():
  parser = argparse.ArgumentParser(description='LED control script',
             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-v', '--verbose', action='count')
  parser.add_argument('-t', '--test', action='store_true',
                      help='Run a basic test sequence.')
  parser.add_argument('-r', '--rate', default=1.0, type=float,
                      help='Approximate rate in seconds for transitions.')
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

  led_array = LedArray(args.red_pin_name, args.green_pin_name,
                       args.blue_pin_name, args.pwm_max_value)
  atexit.register(led_array.__exit__)

  if args.test:
    led_array.test_colors(args.rate)
  elif args.random:
    while(1):
      led_array.random_color(args.rate, True)
  else:
    while(1):
      led_array.color_cycle(args.rate)
     
main()
