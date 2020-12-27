import machine
#from . import config

class Calibrate:
    
    def __init__(self, gyro, display, button):
        self.table_x_adj = 0 
        self.table_y_adj = 0 
        self.wall_x_adj = 0
        self.wall_y_adj = 0
        self.samples = 100
        self.gyro = gyro
        self.display = display
        self.button = button
        

    def cycle(self):
        self.calibrate_level()
    
    
    def setup(self):
        pass
    
    def save_calibration(self):
        with open("main/config.py", 'w') as fp:
            fp.write("TABLE_X_ADJ = " + str(self.table_x_adj) + '\n')
            fp.write("TABLE_Y_ADJ = " + str(self.table_y_adj) + '\n')
            fp.write("WALL_X_ADJ = " + str(self.wall_x_adj) + '\n')
            fp.write("WALL_Y_ADJ = " + str(self.wall_y_adj) + '\n')
        
    
    def calibrate_level(self):
        # TABLE MODE
        self.display.fill(0)
        self.display.text('Lay unit flat on', 0, 0)
        self.display.text('table', 0, 16)
        self.display.text('Press red button', 0, 32)
        self.display.text('to start', 0, 48)
        self.display.show()
        while self.button.value() == 1:
            a = 0

        for i in range(self.samples):
            x_table, y_table, x_wall, y_wall = self.gyro.get_angles()
            self.table_x_adj -= x_table
            self.table_y_adj -= y_table
            self.display.fill(0)
            self.display.text(str(self.samples - i), 60, 32)
            self.display.show()
            
        self.table_x_adj /= self.samples
        self.table_y_adj /= self.samples

        # WALL MODE
        self.display.fill(0)
        self.display.text('Stand unit up ', 0, 0)
        self.display.text('in wall mode', 0, 16)
        self.display.text('Press red button', 0, 32)
        self.display.text('to start', 0, 48)
        self.display.show()
        while self.button.value() == 1:
            a = 0
        for i in range(self.samples):
            x_table, y_table, x_wall, y_wall = self.gyro.get_angles()
            self.wall_x_adj -= x_wall
            self.wall_y_adj -= y_wall
            self.display.fill(0)
            self.display.text(str(self.samples - i), 60, 32)
            self.display.show()
            
        self.wall_x_adj /= self.samples
        self.wall_y_adj /= self.samples

        self.save_calibration()
        self.display.fill(0)
        self.display.show()
        machine.reset()
        
        
            
    
                
                    