############################################################
# Reads accelerometer and calculates x and y angles.
# Prints to onboard OLED
# Prints to Serial bus
############################################################

import framebuf
from . import writer
from . import freesans20


class BubbleLevel:
    
    def __init__(self, accel, display, graphic_mode=False):
        self.accel = accel
        self.display = display
        self.font_writer = writer.Writer(display, freesans20)
        self.graphic_mode = graphic_mode


    def cycle(self, n=1):
        for _ in range(n):
            x_angle, y_angle = self.accel.read_mpu6050()
            if self.graphic_mode:
                self.display_crosshairs(x_angle, y_angle)
            else:
                self.display_data(x_angle, y_angle)
        return True


    def setup(self):
        pass
    
    
    def display_data(self, c_angle_x, c_angle_y):
        
        def write_text(text, line):
            textlen = self.font_writer.stringlen(text)
            self.font_writer.set_textpos(77 - textlen, line)
            self.font_writer.printstring(text)
            
        self.display.fill(0)
        write_text(str(int(abs(c_angle_y))), 0)
        write_text(str(int(abs(c_angle_x))), 32)
        self.add_arrows()
        self.display.show()


    # DELETE for bubble level, keep for inclinometer
    def display_crosshairs(self, c_angle_x, c_angle_y):
        
        def limit_angle(a):
            # a = angle, returns limit of angle or 30 degrees
            if a < -60:
                return 0
            if a < -30:
                return -30
            if a > 60:
                return 0
            if a > 30:
                return 30
            return int(a)
        
        def limit_cross(c, x_coord=True):
            lim = 128 if x_coord else 64
            if c > lim:
                return lim
            if c < 0:
                return 0
            return int(c)
            
        # clear screen
        self.display.fill(0)
        # center of cross
        x = 64 - limit_angle(c_angle_x * -1)
        y = 32 - limit_angle(c_angle_y)
        
        # black out center of cross when at zero
        center = 0 if (x == 64 and y==32) else 1
        # cross vertical lines
        self.display.line(x-2, limit_cross(y-16, False), x-2, limit_cross(y+16, False), 1)
        self.display.line(x-1, limit_cross(y-16, False), x-1, limit_cross(y+16, False), center)
        self.display.line(x, limit_cross(y-16, False), x, limit_cross(y+16, False), center)
        self.display.line(x+1, limit_cross(y-16, False), x+1, limit_cross(y+16, False), center)
        self.display.line(x+2, limit_cross(y-16, False), x+2, limit_cross(y+16, False), 1)

        # cross horizontal lines
        self.display.line(limit_cross(x-16), y-2, limit_cross(x+16), y-2, 1)
        self.display.line(limit_cross(x-16), y-1, limit_cross(x+16), y-1, center)
        self.display.line(limit_cross(x-16), y, limit_cross(x+16), y, center)
        self.display.line(limit_cross(x-16), y+1, limit_cross(x+16), y+1, center)
        self.display.line(limit_cross(x-16), y+2, limit_cross(x+16), y+2, 1)
        # draw crosshairs
        self.display.line(64, 0, 64, 64, 1)
        self.display.line(32, 32, 96, 32, 1)

        self.display.show()
        
    def add_arrows(self):
        # up/down arrows
        def updown(x):
            self.display.line(x, 0, x, 15, 1)

            self.display.line(x, 0, x-4, 4, 1)
            self.display.line(x, 0, x+4, 4, 1)

            self.display.line(x, 15, x-4, 11, 1)
            self.display.line(x, 15, x+4, 11, 1)
        
        
        def sideside(y):
            self.display.line(22, y, 37, y, 1)

            self.display.line(22, y, 26, y-4, 1)
            self.display.line(22, y, 26, y+4, 1)

            self.display.line(37, y, 33, y-4, 1)
            self.display.line(37, y, 33, y+4, 1)
            
        
        updown(30)
        updown(31)
        sideside(40)
        sideside(41)
