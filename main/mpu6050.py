############################################################
# Reads accelerometer and calculates x and y angles.
# Prints to onboard OLED
# Prints to Serial bus
############################################################
import machine, ubinascii, time, math
from machine import Pin, I2C
from time import sleep

# Default I2C address for the MPU6050
# mpu6050_addr = 0x68

# Required MPU6050 registers and their addresses
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
TEMP_OUT_H   = 0X41

class MPU6050:
    
    def __init__(self, i2c, addr=0x68):
        # Globals
        self.last_read_time = 0.0   
        # These are the filtered angles
        self.last_x_angle = 0.0          
        self.last_y_angle = 0.0
        self.last_z_angle = 0.0  
        # Calibrated measurements to offset some bias or error in the readings.
        self.calib_x_accel = 0.0 
        self.calib_y_accel = 0.0 
        self.calib_z_accel = 0.0 
        self.calib_x_gyro  = 0.0 
        self.calib_y_gyro  = 0.0 
        self.calib_z_gyro  = 0.0
        
        self.i2c = i2c
        self.mpu6050_addr=addr
        self.init_MPU()
        self.calibrate_sensors()


    def init_MPU(self):
        #write to sample rate register 
        self.i2c.writeto_mem(self.mpu6050_addr, SMPLRT_DIV, b'\x07')
        #Write to power management register to wake up mpu6050
        self.i2c.writeto_mem(self.mpu6050_addr, PWR_MGMT_1, b'\x00')
        #Write to Configuration register 
        self.i2c.writeto_mem(self.mpu6050_addr, CONFIG, b'\x00')
        #Write to Gyro configuration register to self test gyro 
        self.i2c.writeto_mem(self.mpu6050_addr, GYRO_CONFIG, b'\x18')
        #Set interrupt enable register to 0 .. disable interrupts
        self.i2c.writeto_mem(self.mpu6050_addr, INT_ENABLE, b'\x00')


    def read_raw_data(self, addr):
        #Accelero and Gyro value are 16-bit
        high = self.i2c.readfrom_mem(self.mpu6050_addr, addr, 1)
        #print(ubinascii.hexlify(high))
        low  = self.i2c.readfrom_mem(self.mpu6050_addr, addr+1, 1)
        #print(ubinascii.hexlify(low))
        #concatenate higher and lower values
        val = high[0] << 8 | low[0]
        #we're expecting a 16 bit signed int (between -32768 to 32768). This step ensures 16 bit unsigned int raw readings are resolved. 
        if(val > 32768):
            val = val - 65536
        return val
    

    def read_mpu6050(self):

        try:
            t_now = time.ticks_ms()
            dt = (t_now - self.get_last_time())/1000.0

            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = self.read_values_helper()

            #Full scale range +/- 250 degree/C as per sensitivity scale factor. The is linear acceleration in each of the 3 directions ins g's
            Ax = acc_x/16384.0
            Ay = acc_y/16384.0
            Az = acc_z/16384.0
            
            # This is angular velocity in each of the 3 directions 
            Gx = (gyro_x - self.calib_x_gyro)/131.0
            Gy = (gyro_y - self.calib_y_gyro)/131.0
            Gz = (gyro_z - self.calib_z_gyro)/131.0

            acc_angles = self.acc_angle(Ax, Ay, Az) # Calculate angle of inclination or tilt for the x and y axes with acquired acceleration vectors
            gyr_angles = self.gyr_angle(Gx, Gy, Gz, dt) # Calculate angle of inclination or tilt for x,y and z axes with angular rates and dt 
            (c_angle_x, c_angle_y) = self.c_filtered_angle(acc_angles[0], acc_angles[1], gyr_angles[0], gyr_angles[1]) # filtered tilt angle i.e. what we're after

            self.set_last_read_angles(t_now, c_angle_x, c_angle_y)
            return (c_angle_x, c_angle_y)

        except KeyboardInterrupt:
            pass
            #return (90, 90) # it's never 90 degrees!


    def read_values_helper(self):
        #Read Accelerometer raw value
        acc_x = self.read_raw_data(ACCEL_XOUT_H)
        acc_y = self.read_raw_data(ACCEL_YOUT_H)
        acc_z = self.read_raw_data(ACCEL_ZOUT_H)
        
        #Read Gyroscope raw value
        gyro_x = self.read_raw_data(GYRO_XOUT_H)
        gyro_y = self.read_raw_data(GYRO_YOUT_H)
        gyro_z = self.read_raw_data(GYRO_ZOUT_H)

        #Read Temp raw value
        #temp = self.read_raw_data(TEMP_OUT_H)
        return (acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z)


    def calibrate_sensors(self):
        x_accel = 0
        y_accel = 0
        z_accel = 0
        x_gyro  = 0
        y_gyro  = 0
        z_gyro  = 0
        
        #print("Starting Calibration")
        #Discard the first set of values read from the IMU
        self.read_values_helper()

        # Read and average the raw values from the IMU
        for int in range(10): 
            values = self.read_values_helper()
            x_accel += values[0]
            y_accel += values[1]
            z_accel += values[2]
            x_gyro  += values[3]
            y_gyro  += values[4]
            z_gyro  += values[5]
            time.sleep_ms(10)
        
        x_accel /= 10
        y_accel /= 10
        z_accel /= 10
        x_gyro  /= 10
        y_gyro  /= 10
        z_gyro  /= 10

        # Store the raw calibration values globally
        self.calib_x_accel = x_accel
        self.calib_y_accel = y_accel
        self.calib_z_accel = z_accel
        self.calib_x_gyro  = x_gyro
        self.calib_y_gyro  = y_gyro
        self.calib_z_gyro  = z_gyro

        #print("Finishing Calibration")


    def set_last_read_angles(self, time, x, y):
        #global last_read_time, last_x_angle, last_y_angle
        self.last_read_time = time
        self.last_x_angle = x 
        self.last_y_angle = y
        #last_z_angle = z


    # accelerometer data can't be used to calculate 'yaw' angles or rotation around z axis.
    def acc_angle(self, Ax, Ay, Az):
        radToDeg = 180/3.14159
        ax_angle = math.atan(Ay/math.sqrt(math.pow(Ax,2) + math.pow(Az, 2)))*radToDeg
        ay_angle = math.atan((-1*Ax)/math.sqrt(math.pow(Ay,2) + math.pow(Az, 2)))*radToDeg
        return (ax_angle, ay_angle)


    def gyr_angle(self, Gx, Gy, Gz, dt):
        gx_angle = Gx*dt + self.get_last_x_angle()
        gy_angle = Gy*dt + self.get_last_y_angle()
        gz_angle = Gz*dt + self.get_last_z_angle()
        return (gx_angle, gy_angle, gz_angle)


      # A complementary filter to determine the change in angle by combining accelerometer and gyro values. Alpha depends on the sampling rate...
    def c_filtered_angle(self, ax_angle, ay_angle, gx_angle, gy_angle):
        alpha = 0.75
        c_angle_x = alpha*gx_angle + (1.0 - alpha)*ax_angle
        c_angle_y = alpha*gy_angle + (1.0 - alpha)*ay_angle
        return (c_angle_x, c_angle_y)

     
    def get_last_time(self): 
        return self.last_read_time
    def get_last_x_angle(self):
        return self.last_x_angle
    def get_last_y_angle(self):
        return self.last_y_angle
    def get_last_z_angle(self):
        return self.last_z_angle

