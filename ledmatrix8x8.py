#!/usr/bin/python3
''' Test Bed for Diyhas System Status class '''

import time
from threading import Thread
import random

from Adafruit_Python_LED_Backpack.Adafruit_LED_Backpack import BicolorMatrix8x8

FIBINACCI_MODE = 0
PRIME_MODE = 1
WOPR_MODE = 2
IDLE_MODE = 3
FIRE_MODE = 4
PANIC_MODE = 5

BLACK = 0
GREEN = 1
YELLOW = 3
RED = 2

MAX_DEMO_DISPLAY = 300
MIN_DEMO_DISPLAY = 150

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
          71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
          151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
          233, 239, 241, 251]

class ModeController:
    ''' control changing modes. note Fire and Panic are externally controlled. '''

    def __init__(self, lock):
        ''' create mode control variables '''
        self.bus_lock = lock
        self.current_mode = FIBINACCI_MODE
        self.start_time = time.time()

    def set(self, mode):
        ''' set or override the mode '''
        self.bus_lock.acquire(True)
        self.current_mode = mode
        self.start_time = time.time()
        self.bus_lock.release()

    def get(self,):
        return self.current_mode

    def evaluate(self,):
        ''' initialize and start the fibinnocci display '''
        self.bus_lock.acquire(True)
        if self.current_mode != FIRE_MODE:
            if self.current_mode != PANIC_MODE:
                if self.current_mode != IDLE_MODE:
                    now_time = time.time()
                    elapsed = now_time - self.start_time
                    if elapsed > 30:
                        self.current_mode = self.current_mode +1
                        self.start_time = now_time
                        if self.current_mode > WOPR_MODE:
                            self.current_mode = FIBINACCI_MODE
        self.bus_lock.release()

class FibDisplay:
    '''
        Fibinocci diplay on an 8x8 matrix. Represents 1 to largest 64 bit
        fibinocci number
    '''
    def __init__(self, matrix8x8, lock):
        ''' create the fibinacci object '''
        self.matrix = matrix8x8
        self.bus_lock = lock
        self.iterations = 0
        self.fib1 = 1
        self.fib2 = 1
        self.fib3 = 2

    def activate(self,):
        ''' initialize and start the fibinnocci display '''
        self.bus_lock.acquire(True)
        self.iterations = 0
        self.fib1 = 1
        self.fib2 = 1
        self.fib3 = 2
        self.matrix.set_brightness(5)
        self.bus_lock.release()

    def display(self,):
        ''' display the fibinocci series as a 64 bit image '''
        time.sleep(0.2)
        self.bus_lock.acquire(True)
        # self.matrix.clear()
        for ypixel in range(0, 8):
            for xpixel in range(0, 8):
                self.iterations += 1
                if self.iterations >= 4:
                    self.iterations = 1
                # reg = self.fib3 >> (8 * xpixel)
                # bit = reg & (1 << ypixel)
                reg = self.fib3 >> (8 * xpixel)
                bit = reg & (1 << ypixel)
                if bit == 0:
                    self.matrix.set_pixel(ypixel, xpixel, 0)
                else:
                    self.matrix.set_pixel(ypixel, xpixel, self.iterations)
                    # print("x=", xpixel ," y=", ypixel)
        self.matrix.write_display()
        self.fib1 = self.fib2
        self.fib2 = self.fib3
        self.fib3 = self.fib1 + self.fib2
        if self.fib3 > 7540113804746346429:
            self.fib1 = 1
            self.fib2 = 1
            self.fib3 = 2
        self.bus_lock.release()

class IdleDisplay:
    '''
        Idle diplay on an 8x8 matrix. A slowly moving pixel.
    '''
    def __init__(self, matrix8x8, lock):
        ''' create the idle object '''
        self.matrix = matrix8x8
        self.bus_lock = lock
        self.xpixel = 7
        self.ypixel = 7

    def activate(self,):
        ''' initialize and start the idle display '''
        self.bus_lock.acquire(True)
        self.xpixel = 7
        self.ypixel = 7
        self.matrix.set_brightness(8)
        self.bus_lock.release()

    def display(self,):
        ''' display the moving pixel '''
        time.sleep(1.0)
        self.bus_lock.acquire(True)
        self.matrix.clear()
        self.matrix.set_pixel(self.xpixel, self.ypixel, 0)
        self.ypixel -= 1
        if self.ypixel < 0:
            self.ypixel = 7
            self.xpixel -= 1
            if self.xpixel < 0:
                self.xpixel = 7
        self.matrix.set_pixel(self.xpixel, self.ypixel, 1)
        self.matrix.write_display()
        self.bus_lock.release()

class FlasherDisplay:
    '''
        Flashing display on an 8x8 matrix. Full screen color.
    '''
    def __init__(self, matrix8x8, lock, color):
        ''' create the idle object '''
        self.matrix = matrix8x8
        self.bus_lock = lock
        self.pixel_color = color
        self.toggle = True

    def activate(self,):
        ''' initialize and start the idle display '''
        self.bus_lock.acquire(True)
        self.toggle = True
        self.matrix.set_brightness(15)
        self.bus_lock.release()

    def display(self,):
        ''' display the moving pixel '''
        time.sleep(0.5)
        self.bus_lock.acquire(True)
        if self.toggle:
            color = self.pixel_color
            self.toggle = False
        else:
            color = BLACK
            self.toggle = True
        for xpixel in range(0, 8):
            for ypixel in range(0, 8):
                self.matrix.set_pixel(xpixel, ypixel, color)
        self.matrix.write_display()
        self.bus_lock.release()


class PrimeDisplay:
    '''
        Prime numbers less than 256 display on an 8x8 matrix.
    '''
    def __init__(self, matrix8x8, lock):
        ''' create the prime object '''
        self.matrix = matrix8x8
        self.bus_lock = lock
        self.index = 0
        self.row = 0
        self.iterations = 0

    def activate(self,):
        ''' initialize and start the prime number display '''
        self.bus_lock.acquire(True)
        self.index = 0
        self.row = 0
        self.iterations = 0
        self.matrix.set_brightness(15)
        self.bus_lock.release()

    def display(self,):
        time.sleep(0.2)
        self.bus_lock.acquire(True)
        self.matrix.clear()
        self.index += 1
        if self.index >= len(PRIMES):
            self.index = 0
            self.row = 0
        number = PRIMES[self.index]
        row = self.row
        self.row += 1
        if self.row >= 8:
            self.row = 0
        for xpixel in range(0, 8):
            bit = number & (1 << xpixel)
            if self.iterations == 3:
                self.iterations = 1
            else:
                self.iterations += 1
            if bit == 0:
                self.matrix.set_pixel(row, xpixel, 0)
            else:
                self.matrix.set_pixel(row, xpixel, self.iterations)
        self.matrix.write_display()
        self.bus_lock.release()

class WoprDisplay:
    '''
        Wargames movie computer on an 8x8 matrix.
    '''
    def __init__(self, matrix8x8, lock):
        ''' create the prime object '''
        self.matrix = matrix8x8
        self.bus_lock = lock

    def activate(self,):
        ''' initialize and start the idle display '''
        self.bus_lock.acquire(True)
        self.matrix.set_brightness(15)
        self.bus_lock.release()

    def display(self,):
        time.sleep(0.5)
        self.bus_lock.acquire(True)
        self.matrix.clear()
        for xpixel in range(0, 8):
            for ypixel in range(7, 4, -1):
                bit = random.randint(0, 2)
                if bit == 0:
                    self.matrix.set_pixel(ypixel, xpixel, BLACK)
                else:
                    self.matrix.set_pixel(ypixel, xpixel, RED)
        for xpixel in range(0, 8):
            for ypixel in range(4, 2, -1):
                bit = random.randint(0, 2)
                if bit == 0:
                    self.matrix.set_pixel(ypixel, xpixel, BLACK)
                else:
                    self.matrix.set_pixel(ypixel, xpixel, YELLOW)
        for xpixel in range(0, 8):
            for ypixel in range(2, 1, -1):
                bit = random.randint(0, 2)
                if bit == 0:
                    self.matrix.set_pixel(ypixel, xpixel, BLACK)
                else:
                    self.matrix.set_pixel(ypixel, xpixel, RED)
        for xpixel in range(0, 8):
            for ypixel in range(1, -1, -1):
                bit = random.randint(0,2)
                if bit == 0:
                    self.matrix.set_pixel(ypixel, xpixel, BLACK)
                else:
                    self.matrix.set_pixel(ypixel, xpixel, YELLOW)
        self.matrix.write_display()
        self.bus_lock.release()


class LedMatrix8x8:
    '''
    8x8 lED matrix operations for a diyhas
    '''
    def __init__(self, lock):
        ''' init the 8x8 LED matrix display '''
        self.matrix = BicolorMatrix8x8.BicolorMatrix8x8(address=0x70)
        self.matrix.begin()
        self.bus_lock = lock
        self.mode_controller = ModeController(self.bus_lock)
        self.fib = FibDisplay(self.matrix, self.bus_lock)
        self.fib.activate()
        self.idle = IdleDisplay(self.matrix, self.bus_lock)
        self.idle.activate()
        self.fire = FlasherDisplay(self.matrix, self.bus_lock, RED)
        self.fire.activate()
        self.panic = FlasherDisplay(self.matrix, self.bus_lock, YELLOW)
        self.panic.activate()
        self.prime = PrimeDisplay(self.matrix, self.bus_lock)
        self.prime.activate()
        self.wopr = WoprDisplay(self.matrix, self.bus_lock)
        self.wopr.activate()
        self.matrix8x8_thread = Thread(target=self.matrix8x8_timed_update)
        self.matrix8x8_thread.daemon = True

    def matrix8x8_timed_update(self,):
        ''' update the matrix 8x8 based on mode '''
        while True:
            mode = self.mode_controller.get()
            if mode == FIBINACCI_MODE:
                self.fib.display()
            elif mode == IDLE_MODE:
                self.idle.display()
            elif mode == FIRE_MODE:
                self.fire.display()
            elif mode == PANIC_MODE:
                self.panic.display()
            elif mode == PRIME_MODE:
                self.prime.display()
            elif mode == WOPR_MODE:
                self.wopr.display()
            self.mode_controller.evaluate()

    def set_mode(self, mode, override=False):
        ''' set display mode '''
        if override:
        	self.mode_controller.set(mode)
        current_mode = self.mode_controller.get()
        if current_mode == FIRE_MODE or current_mode == PANIC_MODE:
            return
        self.mode_controller.set(mode)

    def run(self):
        ''' start the matrix 8x8 display updates '''
        self.matrix8x8_thread.start()

if __name__ == '__main__':
    exit()
