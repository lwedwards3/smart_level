from . import mpu6050

Class DuoGyro:
    
    def __init__(self, i2c):
        self.gyro_table = mpu6050.MPU6050(i2c, addr=0x69)
        self.gyro_wall = mpu6050.MPU6050(i2c, addr=0x68)


    def get_angles(self):
        table_x, table_y = self.gyro_table.read_mpu6050()
        wall_x, wall_y = self.gyro_wall.read_mpu6050()
        print(table_x, table_y, wall_x, wall_y)
        return table_x, table_y
    
    
    
    
