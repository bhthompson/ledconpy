#! /usr/bin/python
# LED control library for BeagleBone Black.
# This assumes a tri color LED array is connected to
# three PWM signals on the bone.

import Adafruit_BBIO.PWM as PWM
import csv
import logging
import os
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

  def process_file(self, filename):
    if not os.path.exists(filename):
      logging.warning('File not found')
    else:
      with open(filename, 'rb') as f:
        sequence = csv.reader(f)
        for command in sequence:
          if command[0] == 'f':
            self.fade(int(command[1]), int(command[2]), int(command[3]),
                      float(command[4]))
          elif command[0] == 'i':
            self.led_state(self.red_pin, int(command[1]))
            self.led_state(self.green_pin, int(command[2]))
            self.led_state(self.blue_pin, int(command[3]))
            time.sleep(float(command[4]))
          elif command[0] == 'w':
            time.sleep(float(command[1]))
          elif command[0] == 'r':
            self.random_color()
          else:
            logging.warning('invalid command in file')

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
