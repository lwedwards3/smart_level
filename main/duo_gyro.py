from . import mpu6050

class DuoGyro:
    
    def __init__(self, i2c, print_data=False):
        self.gyro_table = mpu6050.MPU6050(i2c, addr=0x69)
        self.gyro_wall = mpu6050.MPU6050(i2c, addr=0x68)
        self.print_data = print_data


    def standardize_y(self, t_y, w_y):
        # adjust the y outputs so the measurements are consistent
        t_y *= -1
        w_y = 90 - w_y
        return t_y, w_y 


    def get_angles(self):
        
        def fmt_angle(a):
            return "{:.1f}".format(round(a, 1))
        
        table_x, table_y = self.gyro_table.read_mpu6050()
        wall_x, wall_y = self.gyro_wall.read_mpu6050()
        
        t_y = table_y * -1
        w_y = 90 - wall_y 
        
        if self.print_data:
            print(fmt_angle(table_x),
                  fmt_angle(table_y),
                  fmt_angle(wall_x),
                  fmt_angle(wall_y),
                  fmt_angle(t_y),
                  fmt_angle(w_y))

        return table_x, table_y, wall_x, wall_y
    
    
    
    
