############################################################
# Reads accelerometer and calculates x and y angles.
# Prints to onboard OLED
# Prints to Serial bus
############################################################

import framebuf
from . import writer
from . import freesans20



class BubbleLevel:
    
    def __init__(self, gyro, display, graphic_mode=False, debug_mode=False):
        self.gyro = gyro
        self.display = display
        self.font_writer = writer.Writer(display, freesans20)
        self.graphic_mode = graphic_mode
        self.debug_mode = debug_mode
        self.x = 0
        self.sign_x = 0
        self.y = 0
        self.sign_y = 0
        
        self.x_table = 0
        self.y_table = 0
        self.x_wall = 0
        self.y_wall = 0


    def cycle(self, n=1):
        for _ in range(n):
            self.x_table, self.y_table, self.x_wall, self.y_wall = self.gyro.get_angles()
            self.merge_readings()
            
            if self.graphic_mode:
                self.display_crosshairs()
            else:
                self.display_data()
        return True


    def setup(self):
        pass
    
    
    def merge_readings(self):
        def sign(n):
            if n == 0:
                return 0
            return 1 if n > 0 else -1
        
        # convert x
        self.y = min(abs(self.y_table), abs(self.y_wall))
        tbl_greater = 1 if self.y_table > self.y_wall else -1
            
        if int(self.y) == 0:
            sign_abs_min = 0
        else:
            sign_abs_min = sign(self.y_table) if abs(self.y_table) < abs(self.y_wall) else sign(self.y_wall)
        self.sign_y = tbl_greater * sign_abs_min * -1
    
        self.x = abs(self.x_table + self.x_wall)/2
        self.sign_x = sign(int(self.x_table + self.x_wall))
        
        
        
    def display_data(self):
        
        def right_num(n, h_pos, v_pos):
            # converts n to string and prints right-justified at pos
            num = str(int(n))
            h_pos = h_pos - 8 * len(num)
            self.display.text(num, h_pos, v_pos)
        
        
        def write_text(text, line):
            textlen = self.font_writer.stringlen(text)
            self.font_writer.set_textpos(77 - textlen, line)
            self.font_writer.printstring(text)
            
        def limit_angle(angle):
            if angle > 45:
                angle = 90 - angle
            elif angle < -45:
                angle = -90 - angle
            return abs(angle)
            
        self.display.fill(0)
        
        if self.debug_mode:
            self.display.text('Table', 16, 0)
            self.display.text('Wall', 80, 0)
            self.display.text('X:', 0, 16)
            self.display.text('Y:', 0, 48)
            right_num(self.x_table, 56, 16)
            right_num(self.y_table, 56, 48)
            right_num(self.x_wall, 112, 16)
            right_num(self.y_wall, 112, 48)
        else:
            y_angle = limit_angle(self.y * self.sign_y)
            x_angle = limit_angle(self.x * self.sign_x)
            write_text(str(int(y_angle)), 0)
            write_text(str(int(x_angle)), 32)
            self.add_arrows()
        self.display.show()


    # DELETE for bubble level, keep for inclinometer
    def display_crosshairs(self):
        
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
        x = 64 - limit_angle(self.x * self.sign_x * -1)
        y = 32 - limit_angle(self.y * self.sign_y)
        
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
            if self.sign_y == 0:
                self.display.line(x-3, 0, x-3, 15, 1)
                self.display.line(x+3, 0, x+3, 15, 1)
            else:
                self.display.line(x, 0, x, 15, 1)

            if self.sign_y== 1:
                self.display.line(x, 0, x-4, 4, 1)
                self.display.line(x, 0, x+4, 4, 1)

            if self.sign_y == -1:
                self.display.line(x, 15, x-4, 11, 1)
                self.display.line(x, 15, x+4, 11, 1)
        
        
        def sideside(y):
            if self.sign_x == 0:
                self.display.line(22, y-3, 37, y-3, 1)
                self.display.line(22, y+3, 37, y+3, 1)
            else:
                self.display.line(22, y, 37, y, 1)

            if self.sign_x == -1:
                self.display.line(22, y, 26, y-4, 1)
                self.display.line(22, y, 26, y+4, 1)

            if self.sign_x == 1:
                self.display.line(37, y, 33, y-4, 1)
                self.display.line(37, y, 33, y+4, 1)
            
        
        updown(30)
        updown(31)
        sideside(40)
        sideside(41)
