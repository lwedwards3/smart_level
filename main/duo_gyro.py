from . import mpu6050

class DuoGyro:
    
    def __init__(self, i2c):
        self.gyro_table = mpu6050.MPU6050(i2c, addr=0x69)
        self.gyro_wall = mpu6050.MPU6050(i2c, addr=0x68)

    def standardize_y(self, t_y, w_y):
        # adjust the y outputs so the measurements are consistent
        t_y *= -1
        w_y = 90 - w_y
        return t_y, w_y 


    def get_angles(self):
        
        table_x, table_y = self.gyro_table.read_mpu6050()
        wall_x, wall_y = self.gyro_wall.read_mpu6050()
        
        t_y = table_y * -1
        w_y = 90 - wall_y 
        
        print(table_y, t_y, wall_y, w_y)

        return table_x, table_y, wall_x, wall_y
    
    
    
    
