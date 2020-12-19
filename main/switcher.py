from machine import Pin
from machine import I2C
import time
import math
from . import ssd1306
from . import mpu6050
from . import brickbreaker
from . import bubble_level
from . import duo_gyro



class Switcher:
    
    def __init__(self):
        self.i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
        self.display = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.mode_button = Pin(17, Pin.IN, Pin.PULL_UP)
        self.mode_button_previous_value = False
        self.mode_ispressed = False
        
        splash_endtime = time.ticks_ms() + 2000 # 2 second splash screen
        self.splash_screen()    
        
        gyro = duo_gyro.DuoGyro(self.i2c)
        self.modes = []
        self.modes.append(['Bubble Level', bubble_level.BubbleLevel(gyro, self.display, graphic_mode=True)])
        self.modes.append(['Inclinometer', bubble_level.BubbleLevel(gyro, self.display, graphic_mode=False)])
        self.modes.append(['BrickBreaker', brickbreaker.BrickBreaker(gyro, self.display)])
        if self.mode_button.value() == 0:  # press button during startup to add debug mode
            self.modes.append(['Debug mode', bubble_level.BubbleLevel(gyro, self.display, graphic_mode=False, debug_mode=True)])
        self.current_mode = 0
        while time.ticks_ms() < splash_endtime:
            a = 0
        self.cls()
        
        
    def run(self):
        while True:
            mode = self.modes[self.current_mode][1]
            mode.setup()
            keep_going = True
            while not self.debounce():
                if keep_going:
                    keep_going = mode.cycle()
            self.menu()
    
    
    def menu(self):
        def update_display():
            self.display.fill(0)
            for i in range(len(self.modes)):
                self.display.text(self.modes[i][0], 16, 16*i)
            self.display.text(">", 0, 16 * self.current_mode)
            self.display.show()
            
        update_display()
        endtime = time.ticks_ms() + 1500
        while time.ticks_ms() < endtime:
            if self.debounce():
                self.current_mode += 1
                if self.current_mode >= len(self.modes):
                    self.current_mode = 0
                update_display()
                while self.debounce():
                    a = 0
                endtime = time.ticks_ms() + 1500
        return
    
        
        
    def cls(self):
        self.display.fill(0)
        self.display.show()


    def debounce(self):
        self.mode_button_previous_value
        if self.mode_button.value() != self.mode_button_previous_value:
            time.sleep(0.01)
        return not self.mode_button.value()


    def splash_screen(self):
        self.display.fill(1)
        self.display.show()
        time.sleep(0.2)
        self.display.fill(0)
        self.display.text("   SmartLevel", 0, 28)
        self.display.text("     v0.5.2", 0, 42)
        self.display.show()
        
        
        