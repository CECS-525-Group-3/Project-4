import random, re
import tkinter as tk

import serial
import smbus
# import pygame

class Temperature(object):
    def __init__(self):
        self._temperature_value = 0
        self._observers = []

    def get_temperature(self):
        return self._temperature_value

    def set_temperature(self, temperature):
        self._temperature_value = temperature
        for callback in self._observers:
            callback(self._temperature_value)

    def bind_to(self, callback):
        self._observers.append(callback)

class Time(object):
    def __init__(self):
        self._seconds = 0
        self._minutes = 0
        self._hours = 0
        self._observers = []

    def set_time(self, seconds, minutes, hours):
        self._seconds = seconds
        self._minutes = minutes
        self._hours = hours
        self._exec_callbacks()

    def _exec_callbacks(self):
        for callback in self._observers:
            callback(self._seconds, self._minutes, self._hours)

    def bind_to(self, callback):
        self._observers.append(callback)

class TemperatureFrame(tk.Frame):
    def __init__(self, temperature, master=None):
        super().__init__(master)
        self._create_text()
        temperature.bind_to(self._update_temperature)

    def _create_text(self):
        self.temperature_label = tk.Label(self.master, text=u'Renesas: 0\u2109', font=('Arial', 50))
        self.temperature_label.pack(side=tk.RIGHT)

    def _update_temperature(self, temperature):
        self.temperature_label['text'] = u'Renesas: {}\u2109'.format(temperature)

        if(temperature >= 80):
            self.temperature_label['fg'] = 'red'
        else:
            self.temperature_label['fg'] = 'black'

class ThermometerFrame(tk.Frame):
    def __init__(self, temperature, master=None):
        super().__init__(master)
        self.canvas = tk.Canvas(self, width=300, height=800)
        self.canvas.pack(side=tk.LEFT)

        self.photo = tk.PhotoImage(file="thermometer.gif")
        self.canvas.create_image(200, 300, image=self.photo)
        self.canvas.create_oval(200 - 42, 530 - 42, 200 + 42, 530 + 42 , fill='red')
        temperature.bind_to(self.draw_mercury)
    
    def draw_mercury(self, temperature):
        self.canvas.delete('line')
        draw_height = 530 - temperature * 4
        if draw_height <= 80:
            draw_height = 80
        self.canvas.create_line(200, 530, 200, draw_height, width=35, fill='red', tag='line') 

class TimeFrame(tk.Frame):
    def __init__(self, time, master=None):
        super().__init__(master)
        self._create_text()
        time.bind_to(self._update_time)

    def _create_text(self):
        self.time_label = tk.Label(self.master, text='00:00:00', font=('Arial', 50))
        self.time_label.pack(side=tk.BOTTOM)

    def _update_time(self, seconds, minutes, hours):
        self.time_label['text'] = '{:0>2}:{:0>2}:{:0>2}'.format(hours, minutes, seconds)

class Application(tk.Frame):
    def __init__(self, temperature, time, master=None):
        super().__init__(master)
        self.pack()
        self.init_frames(temperature, time)

    def init_frames(self, temperature, time):
        self.temperature_frame = TemperatureFrame(temperature, self)
        self.temperature_frame.pack(side=tk.RIGHT)

        self.themometer_frame = ThermometerFrame(temperature, self)
        self.themometer_frame.pack(side=tk.LEFT)

        self.time_frame = TimeFrame(time, self)
        self.time_frame.pack(side=tk.RIGHT)

def int_to_bcd(x):
    """
    This translates an integer into binary coded decimal >>> int_to_bcd(4) 4
    >>> int_to_bcd(34)
    22
    """

    if x < 0:
        raise ValueError("Cannot be a negative integer")

    bcdstring = ''
    while x > 0:
        nibble = x % 16
        bcdstring = str(nibble) + bcdstring
        x >>= 4
        
    if bcdstring == '':
        bcdstring = 0
    return int(bcdstring)

if __name__ == '__main__':

    root = tk.Tk()
    root.wm_title('Temperature Display')
    root.geometry('1100x700')
    # pygame.mixer.init()
    # pygame.mixer.music.load('blip.mp3')
    ser = serial.Serial('/dev/ttyAMA0', 9600)

    #Init the I2C Serial bus at address 0x68
    bus = smbus.SMBus(1)
    address = 0x68
    
    bus.write_byte_data(address, 0, 0)
    bus.write_byte_data(address, 1, 0)
    bus.write_byte_data(address, 2, 0)
    bus.write_byte_data(address, 3, 0)
    
    temperature = Temperature()
    time  = Time()
    app = Application(temperature, time, master=root)
    
    while True:
        seconds = int_to_bcd(bus.read_byte_data(address, 0))
        minutes = int_to_bcd(bus.read_byte_data(address, 1))
        hours = int_to_bcd(bus.read_byte_data(address, 2))
        day = int_to_bcd(bus.read_byte_data(address, 3))
        time.set_time(seconds, minutes, hours)
        #data = str(ser.readline(), 'utf-8')
        #print(data)
        #if re.match(r'RBUT', data):
        #    print('RIGHT BUTTON PRESSED')
        #elif re.match(r'LBUT', data):
        #    print('LEFT BUTTON PRESSED')
        #elif re.match(r'CBUT', data):
        #    print('CENTER BUTTON PRESSED')

        # temperature.set_temperature(float(data))
        root.after(1000, temperature.set_temperature(random.randrange(0, 100)))
        root.update_idletasks()
        root.update()
        # if(temperature.get_temperature() >= 80):
            # pygame.mixer.music.play()
            # while pygame.mixer.music.get_busy() == True:
                # continue
