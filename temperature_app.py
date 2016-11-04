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

    def difference(self, other_time):
        sec_diff = abs(self._seconds - other_time._seconds)
        min_diff = abs(self._minutes - other_time._minutes)
        hour_diff = abs(self._hours - other_time._hours)
        
        return (sec_diff, min_diff, hour_diff)

    def _exec_callbacks(self):
        for callback in self._observers:
            callback(self._seconds, self._minutes, self._hours)

    def bind_to(self, callback):
        self._observers.append(callback)


class TemperatureFrame(tk.Frame):
    def __init__(self, temperature, label=None, master=None, flash=False):
        super().__init__(master)
        if label is None:
            self.label = 'Unknown'
        else:
            self.label = label
        self.flash = flash
        self.alert_temp = 0
        self._create_text()
        temperature.bind_to(self._update_temperature)

    def set_alert_temp(self, alert_temp):
        self.alert_temp = alert_temp

    def _create_text(self):
        self.temperature_label = tk.Label(self.master, text=u'{}: 0\u2109'.format(self.label), font=('Arial', 50))
        self.temperature_label.pack()

    def _update_temperature(self, temperature):
        self.temperature_label['text'] = u'{}: {}\u2109'.format(self.label, round(temperature, 2))

        if temperature >= self.alert_temp and self.flash:
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
    def __init__(self, time, label=None, master=None, toggeling=False,):
        super().__init__(master)
        self.label = label
        self._create_text()
        time.bind_to(self._update_time)

        if toggeling:
            self._create_toggle_canvas()

    def toggle_hours(self):
        self.toggle_canvas.delete('min')
        self.toggle_canvas.delete('sec')
        self.toggle_canvas.create_line(260, 0, 350, 0, width=5, tags='hour')

    def toggle_minutes(self):
        self.toggle_canvas.delete('hour')
        self.toggle_canvas.delete('sec')
        self.toggle_canvas.create_line(370, 0, 460, 0, width=5, tags='min')

    def toggle_seconds(self):
        self.toggle_canvas.delete('hour')
        self.toggle_canvas.delete('min')
        self.toggle_canvas.create_line(480, 0, 570, 0, width=5, tags='sec')  

    def _create_text(self):
        self.time_label = tk.Label(self.master, text='{}: 00:00:00'.format(self.label), font=('Arial', 50))
        self.time_label.pack()

    def _create_toggle_canvas(self):
        self.toggle_canvas = tk.Canvas(self, width=600, height=10)
        self.toggle_canvas.pack()

    def _update_time(self, seconds, minutes, hours):
        self.time_label['text'] = '{}: {:0>2}:{:0>2}:{:0>2}'.format(self.label, hours, minutes, seconds)


class OptionsFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self._create_widgets()

    def _create_widgets(self):
        alert_temp_label = tk.Label(self, text='Alert Temp')
        alert_temp_label.pack(side=tk.LEFT)
        
        self.alert_temp = tk.StringVar()
        self.alert_temp_entry = tk.Entry(self, textvariable=self.alert_temp)
        self.alert_temp.set('85')
        self.alert_temp_entry.pack(side=tk.LEFT)

    def get_alert_temp(self):
        if self.alert_temp.get() == '':
            return '0'
        return self.alert_temp.get()


class Application(tk.Frame):
    def __init__(self, ren_temperature, rtc_temperature, time, overheat_time, normal_time, time_overheated, master=None):
        super().__init__(master)
        self.pack()
        self.init_frames(ren_temperature, rtc_temperature, time, overheat_time, normal_time, time_overheated)

    def init_frames(self, ren_temperature, rtc_temperature, time, overheat_time, normal_time, time_overheated):
        self.themometer_frame = ThermometerFrame(ren_temperature, self)
        self.themometer_frame.pack(side=tk.LEFT)
        
        self.ren_temperature_frame = TemperatureFrame(ren_temperature, 'Renesas', self, flash=True)
        self.ren_temperature_frame.pack(fill=tk.BOTH)

        self.rtc_temperature_frame = TemperatureFrame(rtc_temperature, 'RTC', self)
        self.rtc_temperature_frame.pack(fill=tk.BOTH)

        self.time_frame = TimeFrame(time, 'Clock', self, toggeling=True)
        self.time_frame.pack(fill=tk.BOTH)

        self.overheat_time_frame = TimeFrame(overheat_time, 'Last Time Overheat', self)
        self.overheat_time_frame.pack(fill=tk.BOTH)

        self.last_normal_time_frame = TimeFrame(normal_time, 'Last Time Normal', self)
        self.last_normal_time_frame.pack(fill=tk.BOTH)

        self.time_overheated_frame = TimeFrame(time_overheated, 'Time Overheated', self)
        self.time_overheated_frame.pack(fill=tk.BOTH)


        self.options_frame = OptionsFrame(self)
        self.options_frame.pack()


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


HOURS = 'HOUR'
MINUTES = 'MINUTE'
SECONDS = 'SECONDS'
address = 0x68
bus = smbus.SMBus(1)
ser = serial.Serial('/dev/ttyAMA0', 9600)

def decrement_unit_time(curr_selected_option, time, bus):
    if curr_selected_option == HOURS:
        hours = int_to_bcd(bus.read_byte_data(address, 2))
        bus.write_byte_data(address, 2, hours - 1)
    elif curr_selected_option == MINUTES:
        minutes = int_to_bcd(bus.read_byte_data(address, 1))
        bus.write_byte_data(address, 1, minutes - 1)
    elif curr_selected_option == SECONDS:
        seconds = int_to_bcd(bus.read_byte_data(address, 0))
        bus.write_byte_data(address, 0, seconds - 1)

def increment_unit_time(curr_selected_option, time, bus):
    if curr_selected_option == HOURS:
        hours = int_to_bcd(bus.read_byte_data(address, 2))
        bus.write_byte_data(address, 2, hours + 1)
    elif curr_selected_option == MINUTES:
        minutes = int_to_bcd(bus.read_byte_data(address, 1))
        bus.write_byte_data(address, 1, minutes + 1)
    elif curr_selected_option == SECONDS:
        seconds = int_to_bcd(bus.read_byte_data(address, 0))
        bus.write_byte_data(address, 0, seconds + 1)

if __name__ == '__main__':

    root = tk.Tk()
    root.wm_title('Temperature Display')
    root.geometry('1100x700')
    
    # pygame.mixer.init()
    # pygame.mixer.music.load('blip.mp3')
     
    bus.write_byte_data(address, 0, 0)
    bus.write_byte_data(address, 1, 0)
    bus.write_byte_data(address, 2, 8)
    bus.write_byte_data(address, 3, 0)
    
    ren_temperature = Temperature()
    rtc_temperature = Temperature()
    time  = Time()
    overheat_time = Time()
    normal_time = Time()
    time_overheated = Time()

    overheat_flag = False
    curr_selected_option = None
    
    app = Application(ren_temperature, rtc_temperature, time, overheat_time, normal_time, time_overheated, master=root)
    
    while True:
        data = ''
        alert_temp = int(app.options_frame.get_alert_temp())
        app.ren_temperature_frame.set_alert_temp(alert_temp)
        
        seconds = int_to_bcd(bus.read_byte_data(address, 0))
        minutes = int_to_bcd(bus.read_byte_data(address, 1))
        hours = int_to_bcd(bus.read_byte_data(address, 2))
        day = int_to_bcd(bus.read_byte_data(address, 3))
        
        time.set_time(seconds, minutes, hours)

        rtc_temp = bus.read_byte_data(address, 17)

        if ser.inWaiting() > 0:
            data = str(ser.readline(ser.inWaiting()), 'utf-8')

        if re.match(r'CBUT', data):
            increment_unit_time(curr_selected_option, time, bus)
            
        elif re.match(r'RBUT', data):
            decrement_unit_time(curr_selected_option, time, bus)
            
        elif re.match(r'LBUT', data):
            if curr_selected_option == HOURS:
                app.time_frame.toggle_minutes()
                curr_selected_option = MINUTES
            elif curr_selected_option == MINUTES:
                app.time_frame.toggle_seconds()
                curr_selected_option = SECONDS
            elif curr_selected_option == SECONDS or curr_selected_option is None:
                app.time_frame.toggle_hours()
                curr_selected_option = HOURS
                
       
        
        rand_num = random.randrange(0, 100)
        root.after(500, ren_temperature.set_temperature(rand_num))
        #root.after(500, rtc_temperature.set_temperature(random.randrange(0, 100)))
        
        # ren_temperature.set_temperature(float(data))
        rtc_temperature.set_temperature(rtc_temp * 1.8 + 32)

        if rand_num > alert_temp:
            overheat_time.set_time(seconds, minutes, hours)
            overheat_flag = True

        if rand_num < alert_temp and overheat_flag:
            normal_time.set_time(seconds, minutes, hours)
            time_diff = normal_time.difference(overheat_time)
            time_overheated.set_time(time_diff[0], time_diff[1], time_diff[2])
            overheat_flag = False
        
        root.update_idletasks()
        root.update()
        
        # if(temperature.get_temperature() >= 80):
            # pygame.mixer.music.play()
            # while pygame.mixer.music.get_busy() == True:
                # continue
