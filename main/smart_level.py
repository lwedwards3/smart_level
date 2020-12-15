from machine import Pin
from machine import I2C
import utime
from . import ssd1306
from . import mpu6050


class SmartLevel:
    
    def __init__(self):
        self.led = Pin(2, Pin.OUT)
        self.led.value(1)
        i2c = I2C(sda=Pin(21, Pin.PULL_UP), scl=Pin(22, Pin.PULL_UP), freq=400000)
        Pin(19, Pin.OUT).value(1) # set AD0 on gyr_flat = high
        self.gyr_flat = mpu6050.MPU6050(i2c, 0x69)     # i2c 105 (AD0=HIGH)
        self.gyr_upright = mpu6050.MPU6050(i2c, 0x68)  # i2c 104 (AD0 not connected)
        self.display = ssd1306.SSD1306_I2C(128, 64, i2c)
        


    def combine(self, x_horz, y_horz, x_vert, y_vert):
        def sign(n):
            return 1 if n>=0 else -1

        x_new = (x_horz+x_vert)/2
        if abs(y_horz) < 30:
            y_new = y_horz
        elif abs(y_horz) < 60:
            y_new = (abs(y_horz) + abs(y_vert)) / 2 * sign(y_horz)
        else:
            y_new = y_vert
        return x_new, y_new
    
    
    def update_display(self, x_horz, y_horz, x_vert, y_vert):
        def fmt(n):
            # Returns a string representation of n,
            # rounded to 1 decimal point.
            return "{:.1f}".format(round(n,1))

        
        def align(vals, n=10):
            s = ""
            if len(vals) == 2:
                s = fmt(vals[0])
                l = 16 - len(fmt(vals[0])) - len(fmt(vals[1]))
                s = s + ' ' *  l
                s = s + fmt(vals[1])
                return s
            for x in vals:
                x = fmt(x)
                s = s + " " * (n - len(x)) + x
            return s
        
        x_new, y_new = self.combine(x_horz, y_horz, x_vert, y_vert)
        g0 = align([x_horz, y_horz], n=7)
        g1 = align([x_vert, y_vert], n=7)
        #g_new = align([x_new, y_new], n=7)

        self.display.fill(0)
        self.display.text(g0, 0, 0)
        self.display.text(g1, 0, 48)
        
        y_display = ' ' * max((14-len(fmt(y_new))),0) + fmt(y_new)
        self.display.text(y_display, 0, 24)
        x_display = ' ' * max((7-len(fmt(x_new))),0) + fmt(x_new)
        self.display.text(x_display, 0, 24)
        
        #display.text(g_new, 0, 48)
        #self.show_arrows(x_new, y_new)
        self.display.show()
        
    def run(self):
        update_time = utime.ticks_ms() + 200
        while True:
            x_horz, y_horz = self.gyr_flat.read_mpu6050()
            x_vert, y_vert = self.gyr_upright.read_mpu6050()
            
            #if debounce(switch) != switch_previous:
            #    switch_previous = not switch_previous
            #    if switch_previous == 1:
            #        config['calibration']['x_horz'] = x_horz
            #        config['calibration']['y_horz'] = y_horz
            #        config['calibration']['x_vert'] = x_vert
            #        config['calibration']['y_vert'] = y_vert
            
            if utime.ticks_ms() >= update_time:
                #x_horz, y_horz, x_vert, y_vert = apply_calibration(x_horz, y_horz, x_vert, y_vert)
                
                self.update_display(x_horz, y_horz, x_vert, y_vert)
                #x_new, y_new = combine_2(x_horz, y_horz, x_vert, y_vert)
                #print(align([x_horz, x_vert, x_new, y_horz, y_vert, y_new, switch_previous]))
                update_time = utime.ticks_ms() + 200
                
            
            #x_horz, y_horz = self.gyr_flat.read_mpu6050()
            #x_vert, y_vert = self.gyr_upright.read_mpu6050()
            #print(x_horz, x_vert, y_horz, y_vert)
