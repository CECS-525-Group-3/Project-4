import random
import tkinter as tk

# import serial
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

class TemperatureFrame(tk.Frame):
    def __init__(self, temperature, master=None):
        super().__init__(master)
        self._create_text()
        temperature.bind_to(self._update_temperature)

    def _create_text(self):
        self.temperature_label = tk.Label(self.master, text=u'0\u2109', font=('Arial', 200))
        self.temperature_label.pack(side=tk.RIGHT)

    def _update_temperature(self, temperature):
        self.temperature_label['text'] = u'{}\u2109'.format(temperature)

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
    def __init__(self, hours, minutes, seconds, master=None):
        super().__init__(master)
        self._create_text()

    def _create_text(self):
        self.time_label = tk.Label(self.master, text='00:00:00', font=('Arial', 50))
        self.time_label.pack(side=tk.BOTTOM)

class Application(tk.Frame):
    def __init__(self, temperature, master=None):
        super().__init__(master)
        self.pack()
        self.init_frames(temperature)

    def init_frames(self, temperature):
        self.temperature_frame = TemperatureFrame(temperature, self)
        self.temperature_frame.pack(side=tk.TOP)

        self.themometer_frame = ThermometerFrame(temperature, self)
        self.themometer_frame.pack(side=tk.LEFT)

        self.time_frame = TimeFrame(0, 0, 0, self)
        self.time_frame.pack(side=tk.BOTTOM)

if __name__ == '__main__':

    root = tk.Tk()
    root.wm_title('Temperature Display')
    root.geometry('1100x700')
    # pygame.mixer.init()
    # pygame.mixer.music.load('blip.mp3')
    # ser = serial.Serial('/dev/ttyAMA0', 9600)

    temperature = Temperature()
    app = Application(temperature, master=root)
    
    while True:
        # data = ser.readline()
        # temperature.set_temperature(float(data))
        root.after(1000, temperature.set_temperature(random.randrange(0, 100)))
        root.update_idletasks()
        root.update()
        # if(temperature.get_temperature() >= 80):
            # pygame.mixer.music.play()
            # while pygame.mixer.music.get_busy() == True:
                # continue