# This will import all the widgets
# and modules which are available in
# tkinter and ttk module
from tkinter import * 
from tkinter import messagebox
from tkinter.ttk import *
from numpy.lib.function_base import angle
import serial
import serial.tools.list_ports
from threading import Thread
from time import sleep
import numpy as np
import trace
from PIL import ImageTk, Image
import socket
import json
from general_functions import *
import sys

# creates a Tk() object
master = Tk()

ready = False
arduino = ""
angles_raw = [0]*20
angles = [0]*24
angle_calibration = [0,45,90]

# Variables for calibration
x_MCP = [[0] * 3 for i1 in range(5)]
x_PIP = [[0] * 3 for i1 in range(5)]
z_MCP = [0]*7
coeff_MCP = [[0] * 3 for i1 in range(5)]
coeff_PIP = [[0] * 3 for i1 in range(5)]
done = True
val = 0

#----------------------------function/thread for the interface--------------------------#
def interface():
    global master
    master.title("E.D.A.S")
    master.state('zoomed')
    ports = serial.tools.list_ports.comports(include_links=False)
    if (len(ports) != 0): # on a trouvé au moins un port actif
        label = Label(master, text ="Choose the port to which the device is connected:", font=("Courier", 20)).pack(pady = 10)
        for port in ports :  # affichage du nom de chaque port
            Button(master, text = port.device, command = lambda : Calibration(port.device)).pack(pady = 10)
    else:  
        label = Label(master, text = "No port found.").pack(pady = 10)
        label = Label(master, text = "Connect a device and relaunch the interface.").pack(pady = 10)
        
def Calibration(portDevice):
    global master
    global ready
    global arduino
    arduino = serial.Serial(port=portDevice, baudrate=9600, timeout=.1)
    ready = True
    eraseWidget()
    try:
        with open("c:/TRAVAIL/MSc project/code python/sample.json") as json_open:
            data = json.load(json_open)
        Label(master, text ="Do you want to calibrate or use a previous calibration profile?", font=("Courier", 20)).pack()
        Button(master, text = "New calibration", command = Cal).pack(pady = 10)
        Button(master, text = "Use a user calibration profile", command = NoCal).pack(pady = 10)
    except:
        Label(master, text ="You didn't calibrate yet... Create a new calibration", font=("Courier", 20)).pack()
        Button(master, text = "New calibration", command = Cal).pack(pady = 10)


def Cal():
    global master
    global val
    eraseWidget()

    if val == 0:
        Label(master, text ="Put your finger at 0° and close to each other", font=("Courier", 20)).pack()
        image1 = Image.open("c:/TRAVAIL/MSc project/code python/main.jpg")
        image1 = image1.resize((300, 475), Image.ANTIALIAS)
        test = ImageTk.PhotoImage(image1)
        label1 = Label(image=test)
        label1.image = test
        label1.place(x=master.winfo_screenwidth()/2-300/2, y=master.winfo_screenheight()/2-475/2)
    if val == 1:
        Label(master, text ="Put your finger at 45°", font=("Courier", 20)).pack()
    if val == 2:
        Label(master, text ="Put your finger at 90°", font=("Courier", 20)).pack()
    if val == 3:
        Label(master, text="UserName", font=("Courier", 20)).pack()
        entry1 = Entry(master, font=("Courier", 20))
        entry1.pack()
        Button(master, text = "Submit!", command = lambda : getName(entry1.get())).pack()
    if val<3:
        Button(master, text = "Done!", command = lambda : get_calibration(val)).place(x=725, y=700)

def get_calibration(num):
    global angles_raw, val, coeff_MCP,coeff_PIP
    eraseWidget()
    if num==0:
        for i in range(0,7):
            z_MCP[i] = angles_raw[i+11]
    for j in range(0,5):
        x_MCP[j][num] = angles_raw[j]
        x_PIP[j][num] = angles_raw[j+5]
    val = val + 1
    if val == 3:
        for t in range(0,5):
            coeff_MCP[t] = np.polyfit(x_MCP[t],angle_calibration,2).tolist()
            coeff_PIP[t] = np.polyfit(x_PIP[t],angle_calibration,2).tolist()
    Cal()

def getName(name):
    try:
        with open("c:/TRAVAIL/MSc project/code python/sample.json") as json_open:
            data = json.load(json_open)

        data['Usernames'].append({'name': name,'PIP': coeff_MCP,'MPCx': coeff_MCP,'MPCz': z_MCP})

        with open("c:/TRAVAIL/MSc project/code python/sample.json","w") as json_write:
            json.dump(data,json_write)
    except:
        data = {}
        data['Usernames'] = []
        data['Usernames'].append({'name': name,'PIP': coeff_MCP,'MPCx': coeff_MCP,'MPCz': z_MCP})

        with open("c:/TRAVAIL/MSc project/code python/sample.json", "w") as json_create:
            json.dump(data, json_create)
    final_page()

def NoCal():
    eraseWidget()
    Label(master, text ="Choose your calibration profile", font=("Courier", 20)).pack()
    with open("c:/TRAVAIL/MSc project/code python/sample.json") as json_open:
        data = json.load(json_open)
    for user in data['Usernames'] :  # button of the name of the user
        Button(master, text = user['name'], command = lambda : get_coeff(user['PIP'],user['MPCx'],user['MPCz'])).pack(pady = 10)

# function that replace the coefficient from the JSON
def get_coeff(PIP, MPCx, MPCz):
    global coeff_MCP, coeff_PIP, z_MCP
    coeff_MCP = MPCx
    coeff_PIP = PIP
    z_MCP = MPCz
    final_page()

def final_page():
    eraseWidget()
    Label(master, text ="You are ready to use the glove", font=("Courier", 20)).pack()
    Label(master, text ="The angles are avaibles in the array 'angles'", font=("Courier", 20)).pack()

def Unity():
    eraseWidget()
    '''host, port = "127.0.0.1", 25001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))'''
    print('Connected to UNITY')


#---------------function/thread to read the data from the serial port----------------#
class thread_with_trace(Thread):
  def __init__(self, *args, **keywords):
    Thread.__init__(self, *args, **keywords)
    self.killed = False
  
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run      
    Thread.start(self)
  
  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
  
  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None
  
  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace
  
  def kill(self):
    self.killed = True
  
def func():
  while True:
    global ready
    global angles_raw
    global angles
    if ready == True:
        data = arduino.readline()[:-2]
        if data:
            angles_raw = [float(x) for x in data.split()] 
            print(angles_raw)
            for i in range (0,5):
                # PIP
                angles[i] = poly_reg(coeff_PIP[i], angles_raw[i])
                # MCPx
                angles[i+5]= poly_reg(coeff_MCP[i],angles_raw[i+5])
            for i in range (0,7):
                # MCPz
                angles[i+10] = (potToAngle(angles_raw[i+10])-z_MCP[i])
            for i in range(0,3):
                #IMU angles
                angles[i+17] = angles_raw[i+17]
            for i in range (0,4): 
                # DIP
                angles[i+20] = angles[i+1]*0.88
            print(angles)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        thread.kill()
        master.quit()

def eraseWidget():
    for widgets in master.winfo_children():
        widgets.destroy()

if __name__ == "__main__":
    thread2 = Thread(target = interface)
    thread = thread_with_trace(target = func)
    thread2.start()
    thread.start()
    master.protocol("WM_DELETE_WINDOW", on_closing)
    master.mainloop()