import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
import numpy as np
from time import sleep
from pyftdi.i2c import I2cController
i2c = I2cController()
# Ftdi().open_from_url(’ftdi:///?’)
i2c.configure('ftdi://ftdi:232h:0:ff/1')
slave = i2c.get_port(0x68)
#set MPU6050 Registers through their Address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47


vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

def Cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def init():
    # Write to sample rate register
    slave.write_to(SMPLRT_DIV, b'\x07')
    # Write to power management register
    slave.write_to(PWR_MGMT_1, b'\x01')
    # Write to Configuration register
    slave.write_to(CONFIG, b'\x00')
    # Write to Gyro configuration register
    slave.write_to(GYRO_CONFIG, b'\x18')
    # Write to interrupt enable register
    slave.write_to(INT_ENABLE, b'\x01')

devAddr = 0x68 # MPU6050 device Address

init()
print("Gyroscope and Accelerometer Data:")

def getData(addr):
    #16-bit sensor data, in higher byte and lower byte
    hi = slave.read_from(addr, 1).hex()
    lo = slave.read_from(addr + 1, 1).hex()
    value = int(hi + lo, 16)

    if(value > 32768):
        value = value - 65536
    return value


def translateAngles(acc):
    if(acc < 0.1 and acc > -0.1):
        return(0)

    if(acc < 1.1 and acc > 0.9):
        return(0)

    return(acc)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0, 0.0, -5)

    while True:
        #for i in range(30):
        #Read Accelerometer raw value
        xAcc = getData(ACCEL_XOUT_H)
        yAcc = getData(ACCEL_YOUT_H)
        zAcc = getData(ACCEL_ZOUT_H)
        # print(xAcc, yAcc, zAcc)
        #Read Gyroscope raw value
        xGyro = getData(GYRO_XOUT_H)
        yGyro = getData(GYRO_YOUT_H)
        zGyro = getData(GYRO_ZOUT_H)
        # print(xGyro, yGyro, zGyro)
        #Full scale range +/- 250 degree/C as per sensitivity scale factor
        xA = xAcc/16384.0
        yA = yAcc/16384.0
        zA = zAcc/16384.0
        xG = xGyro/131.0
        yG = yGyro/131.0
        zG = zGyro/131.0
        print('--------')
        print("xG, yG, zG = %.2f, %.2f, %.2f \u00b0/s" %(xG, yG, zG))
        print("xA, yA, zA = %.2f, %.2f, %.2f g" %(xA, yA, zA))
        sleep(0.1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        #xA, yA, zA = translateAngles(xA), translateAngles(yA), translateAngles(zA)
        offset = -5
        glRotatef(0.0,0.0,1.0,0.0)
        glRotatef(yA*offset, 1.0, 0.0, 0.0)
        glRotatef(offset*xA, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        Cube()
        pygame.display.flip()
        pygame.time.wait(1)

main()


