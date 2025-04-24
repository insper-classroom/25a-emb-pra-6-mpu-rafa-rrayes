
import serial
import struct
import pyautogui as pg
from time import sleep, time
pg.PAUSE = 0

class Pointer:
    def __init__(self, port, baud_rate=115200, speed=2, delay=50):
        self.port = port
        self.baud_rate = baud_rate
        self.com = serial.Serial(self.port, self.baud_rate)

        self.dx_zero = 0
        self.dy_zero = 0

        self.speed = speed
        self.delay = delay/1000
        
    def open_port(self):
        self.com.reset_input_buffer()
        self.com.open()
    def close_port(self):
        self.com.close()
    def parse_data(self, pkt):
        axis, raw_value, end = struct.unpack('>BhB', pkt)
        return axis, -raw_value, end
    def norm_x(self, a):
        return ((a-345)*(a>0)+(a<=0)*(a*-1 - 90))/10
    
    def norm_y(self, a):
        return ((a - 258)*(a > 0)+a*(a <= 0))/10
    def calibrate(self):

        input("Segure o ponteiro perpendicular a tela\nDe enter quando estiver pronto!")
        self.dx_zero, self.dy_zero = self.get_mean()
        print("Foi!")
        
    def get_mean(self, duration=2):
        self.com.reset_input_buffer()

        start = time()

        mean_dx = []
        mean_dy = []
        while time()-start < duration:

            pkt = self.com.read(4)
            if len(pkt) != 4:
                continue

            axis, value, end = self.parse_data(pkt)
        
            if end != 0xFF:
                continue

            if axis == 0:
                mean_dx.append(self.norm_x(value))
            elif axis == 1:
                mean_dy.append(self.norm_y(value))
            sleep(self.delay)
        mean_dx = sum(mean_dx)/len(mean_dx)
        mean_dy = sum(mean_dy)/len(mean_dy)
        return mean_dx, mean_dy
    
    def start_pointer(self, duration):
        self.com.reset_input_buffer()
        start = time()
        while time()-start < duration:
            pkt = self.com.read(4)
            if len(pkt) != 4:
                continue

            axis, value, end = self.parse_data(pkt)
            print(axis, value, end)
            if end != 0xFF:
                continue

            if axis == 0:
                pg.moveRel((self.norm_x(value)-self.dx_zero)*self.speed, 0, duration=self.delay)
            elif axis == 1:
                pg.moveRel(0, (self.norm_y(value)-self.dy_zero)*self.speed, duration=self.delay)
            elif axis == 2:
                pg.click()
        
    


pt = Pointer('/dev/cu.usbmodem102', 115200)
pt.start_pointer(5)
pt.calibrate()
pt.start_pointer(10)