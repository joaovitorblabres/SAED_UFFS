import copy
import csv
import numpy as np
import time
import tkinter as tk
import time, codecs
import matplotlib.animation as animation
import matplotlib
import matplotlib.pyplot as plt
import threading
import serial, serial.rs485
from math import *
from numpy import *
try:
    from Tkinter import *
except ImportError:
    from tkinter import *
from tkinter import BOTH, END, LEFT, font, N, NE, NW, W, S, SE, E
from tkinter import ttk, filedialog, StringVar, IntVar
from tkinter import messagebox as tkMessageBox
from numpy.linalg import inv
from scipy.optimize import curve_fit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from PIL import ImageTk, Image
from datetime import datetime
from multiprocessing import Process
'''
ser3 = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)'''
# ser.isOpen()
## TESTES COM VIRTUALIZACAO
#ser2 = serial.Serial(
#    port='/dev/tnt0',
#    baudrate=9600,
#    parity=serial.PARITY_ODD,
#    stopbits=serial.STOPBITS_TWO,
#    bytesize=serial.EIGHTBITS
#)
def receive():
    while(1):
        leng = 0
        reading = ' '
        try:
            ser3.flushInput()
            reading = ser3.readline()
            saida = ''
        except:
            print("Erro de leitura, confira a conexão")
            time.sleep(2)
        leng = len(reading)
        if(reading[0] == ":" and leng >= 6*4+1 and reading[leng-1] == "|"):
            try:
                readed2str = bytearray(reading)
                #reading.replace('\xad', '')
                try:
                    readed2str[:1].decode()
                except:
                    del readed2str[0]
                for i in range(1, leng, 4):
                    saida += readed2str.decode()[i]
                    saida += readed2str.decode()[i+1]
                    saida += readed2str.decode()[i+2]
                    saida += readed2str.decode()[i+3]
                readed = codecs.decode(saida, "hex")
                readed = readed.decode("utf-8")
                complete = []
                fileName = "temperature_" + readed[0] + "_" + Application.strDate + ".csv"
                media = 0
                tSensores = 6
                for i in range(0, tSensores): # -0 a +100
                    val = float(readed[1].split(';')[i])*100/1024
                    complete.append(val)
                    media += val
                media /= tSensores
                j = 1
                print(complete)
                for b in complete:
                    if((b < (media - 25)) or (b > (media + 25))):
                        tkMessageBox.showerror("Atencao", "Sensor " + str(j) +" esta com um diferenca grande de temperatura em relacao aos demais")
                    elif((b < (media - 10)) or (b > (media + 10))):
                        tkMessageBox.showwarning("Atencao","Sensor " + str(j) +" esta com um diferenca pequena de temperatura em relacao aos demais")
                    j += 1
                with open(fileName, 'a') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(complete[:Application.sensor])
                    csvfile.close()
                time.sleep(1)
            except:
                print("Erro de conversão, aguarde a próxima tentativa")
        else:
            print("Erro na recebimento")
        try:
            ser3.close()
            time.sleep(2)
            ser3.open()
        except:
            print("Problema no serial, reiniciando")
            try:
                ser3.open()
            except:
                pass

tempera = threading.Thread(target=receive, daemon=True)

class Application(tk.Frame):
    tempTotal = []
    yTotal = []
    t = 0
    sensor = 5
    boards = 1
    intervalo = 6
    filesPath = "./"
    qtdLeituras = 10
    dt = datetime.now()
    tt = dt.timetuple()
    i = 0
    strDate = ""

    for it in tt:
        if(i < 4):
            strDate += str(it) + "_"
        if(i == 4):
            strDate += str(it)
        i += 1

    for kl in range(1, boards+1):
        Board = "B" + str(kl)
        fileName = "temperature_" + Board + "_" + strDate + ".csv"
        with open(fileName, 'a') as csvfile:
            pass

    def __init__(self, master=None):
        super().__init__(master)
        self.typeTemp = tk.StringVar()
        self.typeTemp.set("0")
        self.chargeConfFile()
        self.confs()
        self.pack()
        self.create_widgets()

    def confs(self):
        self.master.title("Software SAED")
        self.master.maxsize(1000, 800)
        self.master.minsize(1000, 800)
        self.master.configure(background="#d3d3d3")

    def onClick(self):
        global pause
        pause ^= True
        if not pause:
            self.play.config(image=self.pausePng)
            self.play.image = self.pausePng
        else:
            self.play.config(image=self.playPng)
            self.play.image = self.playPng

    def create_widgets(self):
        self.configure(background="#d3d3d3")
        self.CheckVar0 = IntVar()
        self.CheckVar0.set(1)
        self.CheckVar1 = IntVar()
        self.CheckVar1.set(1)
        self.CheckVar2 = IntVar()
        self.CheckVar2.set(1)
        self.CheckVar3 = IntVar()
        self.CheckVar3.set(1)
        self.CheckVar4 = IntVar()
        self.CheckVar4.set(1)
        self.CheckVar5 = IntVar()
        self.CheckVar5.set(1)
        global tempera
        #tempera.start()
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=W, pady=5, padx=5)

        #self.canvas._tkcanvas.pack(side=tk.LEFT, expand=True)

        self.lbBoards = tk.Label(self, text = "SAED", font=("default", 20))
        self.lbBoards.grid(row=0, column=0, sticky=W)

        self.image = Image.open("files/conf.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.confPng = ImageTk.PhotoImage(self.image)
        self.image = Image.open("files/exit.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.exitPng = ImageTk.PhotoImage(self.image)
        self.image = Image.open("files/play.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.playPng = ImageTk.PhotoImage(self.image)
        self.image = Image.open("files/pause.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.pausePng = ImageTk.PhotoImage(self.image)
        self.image = Image.open("files/upload.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.uplPng = ImageTk.PhotoImage(self.image)
        #self.image = Image.open("files/logoUFFS.png")
        self.logoUFFSPng = tk.PhotoImage(file="files/logoUFFS.png")

        self.confs = tk.Button(self, command=self.configuracoes)
        self.confs.config(image=self.confPng)
        self.confs.image = self.confPng
        self.confs.grid(row=0, column=2, sticky=NE)

        self.upload = tk.Button(self, command=self.importFile)
        self.upload.config(image=self.uplPng)
        self.upload.image = self.uplPng
        self.upload.grid(row=0, column=1, sticky=NE)

        self.quit = tk.Button(self, command=root.destroy)
        self.quit.config(image=self.exitPng)
        self.quit.image = self.exitPng
        self.quit.grid(row=3, column=2, sticky=E)

        self.play = tk.Button(self, command=self.onClick)
        self.play.config(image=self.playPng)
        self.play.image = self.playPng
        self.play.grid(row=3, column=1, sticky=E)

        self.buttons = tk.Frame(self)
        self.buttons.grid(row=1, column=1, sticky="nsew")
        self.buttonSensor0 = tk.Checkbutton(self.buttons, text="Sensor 0", variable = self.CheckVar0, onvalue = 1, offvalue = 0, height = 3)
        self.buttonSensor0.pack(side="top")
        self.buttonSensor1 = tk.Checkbutton(self.buttons, text="Sensor 1", variable = self.CheckVar1, onvalue = 1, offvalue = 0, height = 3)
        self.buttonSensor1.pack(side="top")
        self.buttonSensor2 = tk.Checkbutton(self.buttons, text="Sensor 2", variable = self.CheckVar2, onvalue = 1, offvalue = 0, height = 3)
        self.buttonSensor2.pack(side="top")
        self.buttonSensor3 = tk.Checkbutton(self.buttons, text="Sensor 3", variable = self.CheckVar3, onvalue = 1, offvalue = 0, height = 3)
        self.buttonSensor3.pack(side="top")
        self.buttonSensor4 = tk.Checkbutton(self.buttons, text="Sensor 4", variable = self.CheckVar4, onvalue = 1, offvalue = 0, height = 3)
        self.buttonSensor4.pack(side="top")
        self.buttonSensor5 = tk.Checkbutton(self.buttons, text="Sensor 5", variable = self.CheckVar5, onvalue = 1, offvalue = 0, height = 3)
        self.buttonSensor5.pack(side="top")

        self.logo = tk.Label(self, image = self.logoUFFSPng) #, background='#00693e'
        self.logo.config(image=self.logoUFFSPng)
        self.logo.image = self.logoUFFSPng
        self.logo.grid(row=3, column=0, sticky=W)

        self.mlb = MultiListbox(self, (('DATA_HORA', 20), ('Sensor 0', 8), ('Sensor 1', 8), ('Sensor 2', 8), ('Sensor 3', 8), ('Sensor 4', 8), ('Sensor 5', 8)))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,30) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,31) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,32) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,33) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,34) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,35) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,36) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,37) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,38) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,39) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,40) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,41) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,42) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,43) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,44) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.insert(END, ('%02d/%02d/%04d_%02d:%02d:%02d' % (6,6,2019,11,11,45) , 39.5508, 41.5039, 41.5039, 41.9922, 43.9453, 41.5039))
        self.mlb.grid(row=2, column=0, pady=5)


    def importFile(self):
        pack = filedialog.askopenfilename(initialdir = self.filesPath)
        print(pack)
        if(pack != "()"):
            animate(1, pack)

    def configuracoes(self):
        x = self.winfo_x()
        y = self.winfo_y()
        self.toplevel = tk.Toplevel()
        self.toplevel.geometry("%dx%d+%d+%d" % (300, 200, x + 150, y + 150))
        #self.toplevel.maxsize(450, 350)
        self.toplevel.minsize(650, 450)

        self.infos = tk.Label(self.toplevel, text="Software SAED\n(SISTEMA DE AQUISICAO ELETRONICA DE DADOS EXPERIMENTAIS)").pack(padx=5, pady=10)

        self.lbBoards = tk.Label(self.toplevel, text = "Quantidade de placas (padrao 1):")
        self.lbBoards.pack(expand=1, pady=2)
        self.Boards = tk.Entry(self.toplevel)
        self.Boards.delete(0, END)
        self.Boards.insert(0, self.boards)
        self.Boards.pack(expand=1, pady=2)

        self.lbSens = tk.Label(self.toplevel, text = "Quantidade sensores por placa (padrao 6):")
        self.lbSens.pack(expand=1, pady=2)
        self.sensors = tk.Entry(self.toplevel, text = self.sensor)
        self.sensors.delete(0, END)
        self.sensors.insert(0, self.sensor)
        self.sensors.pack(expand=1, pady=2)

        self.lbInterval = tk.Label(self.toplevel, text = "Intervalo de aferimento de temperatura (em segundos):")
        self.lbInterval.pack(expand=1, pady=2)
        self.interv = tk.Entry(self.toplevel, text = self.intervalo)
        self.interv.delete(0, END)
        self.interv.insert(0, self.intervalo)
        self.interv.pack(expand=1, pady=2)

        self.lbPath = tk.Label(self.toplevel, text = "Local para salvar os dados:")
        self.lbPath.pack(expand=1, pady=2)
        self.paths = tk.Label(self.toplevel, text = self.filesPath)
        self.paths.pack(expand=1, pady=2)
        self.pathB = tk.Button(self.toplevel, text = "Selecionar", command=self.changePath)
        self.pathB.pack(expand=1, pady=2)

        self.getTemperature = tk.Button(self.toplevel, text="Confirmar", font = "Verdana 10 bold", command=self.saveConfs)
        self.getTemperature.pack()

        self.info2 = tk.Label(self.toplevel, text="Em caso de problemas contatar Prof. Pedro Borges").pack(padx=5, pady=10)

        self.wait_window(self.getTemperature)

    def changePath(self):
        self.filesPath = filedialog.askdirectory(initialdir = self.filesPath)
        self.paths['text'] = self.filesPath
        print(self.filesPath)

    def saveConfs(self):
        try:
            self.boards = int(self.Boards.get())
            self.sensor = int(self.sensors.get())
            self.intervalo = int(self.interv.get())
            #.qtdLeituras = int(self.leituras.get())
            tkMessageBox.showinfo("Salvo", "Salvo com sucesso", parent = self.toplevel)
            self.toplevel.destroy()
        except ValueError:
            tkMessageBox.showwarning("Tipo invalido", "As quantidades devem ser numeros inteiros", parent = self.toplevel)

    def getFile(self, fileName):
        with open(fileName, 'r') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reversed(spamreader):
                med = row.rstrip('\n').rstrip('=').split(';')
        return med

    def chargeConfFile(self):
        global globInter
        file = open('files/confs.con', 'r')
        lines = [line.rstrip('\n') for line in file]
        self.sensor = int(lines[0])
        self.boards = int(lines[1])
        self.intervalo = int(lines[2])
        globInter = int(lines[2])
        self.filesPath = lines[3]
        self.typeTemp.set(lines[4])
        self.qtdLeituras = int(lines[5])
        file.close()

    def saveConfFile(self):
        file = open('files/confs.con', 'w')
        file.write(str(self.sensor))
        file.write("\n")
        file.write(str(self.boards))
        file.write("\n")
        file.write(str(self.intervalo))
        file.write("\n")
        file.write(str(self.filesPath))
        file.write("\n")
        file.write(str(self.typeTemp.get()))
        file.write("\n")
        file.write(str(self.qtdLeituras))
        file.write("\n")
        file.close()

class MultiListbox(Frame):
    def __init__(self, master, lists):
        Frame.__init__(self, master)
        self.lists = []
        for l,w in lists:
            frame = Frame(self); frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0,
                         relief=FLAT, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
        frame = Frame(self); frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)
        self.lists[0]['yscrollcommand']=sb.set

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return 'break'

    def _button2(self, x, y):
        for l in self.lists: l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self.lists: l.scan_dragto(x, y)
        return 'break'

    def _scroll(self, *args):
        for l in self.lists:
            l.yview(*(args))

    def curselection(self):
        return self.lists[0].curselection(  )

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))
        if last: return map(*([None] + result))
        return result

    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size(  )

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)

f = Figure(figsize=(6,3.5), dpi=100)
a = f.add_subplot(1, 1, 1)
pCounter = 0
globInter = 0

def func(x, a, c, d):
    return a*np.exp(-c*x)+d

def frange(a, b, p = 0.01):
	l = []
	while a <= b:
		l.append(a)
		a += p
	return l

def mountFuncTeste(a, c, d):
    return "{}*exp(-{}*x)+{}".format(a, c, d)

def expo(X, Y):
    x = np.array(X)
    y = np.array(Y)
    popt, pcov = curve_fit(func, x, y, p0=(1, 1e-2, 1e-2), maxfev=50000)
    xx = np.linspace(x[0]-60, len(x)*10+60, 1000)
    yy = func(xx, *popt)
    print(mountFuncTeste(*popt))
    a.set_xlim(x[0]-10, x[len(x)-1]+10)
    a.set_ylim(y[len(y)-1]-10, y[0]+10)
    a.set_title(mountFuncTeste(*popt), fontsize=11)
    f2 = lambda x : eval(mountFuncTeste(*popt))
    a.plot([x for x in frange(int(x[0])-10, int(x[len(x)-1])+10)], [f2(x) for x in frange(int(x[0])-10, int(x[len(x)-1])+10)], label="Fitted Curve")
    plt.show()

dataList = []
pause = True

def animate(i = 1, name = ""):
	i = 1
	global pause
	if not pause:
	    global dataList
	    if(name == ""):
	        Board = "B1"
	        fileName = "temperature_" + Board + "_" + Application.strDate + ".csv"
	        pullData = open(fileName,"r").read()
	        lastData = pullData.split('\n')[-1]
	        dataList += lastData
	    else:
	        fileName = name
	        pullData = open(fileName,"r").read()
	        dataList = pullData.split('\n')

	    Application.tempTotal = []
	    Application.yTotal = []
	    a.clear()
	    for line in dataList:
	        if line:
	            lines = line.strip().split(';')
	            try:
	                lines = list(map(float, lines[1:]))
	                Application.tempTotal.append(sum(lines)/len(lines))
	                Application.yTotal.append(i*globInter)
	            except Exception as e:
	                pass

	            i += 1
	    Application.t = i
	    a.set_xlabel('Time')
	    a.set_ylabel('Temperature (C)')
	    a.plot(Application.yTotal, Application.tempTotal, 'ro')
	    plt.show()
	    if(Application.t > 8):
	        expo(Application.yTotal, Application.tempTotal)


root = tk.Tk()
app = Application(master=root)
ani = animation.FuncAnimation(f, animate, interval=Application.intervalo*1000)
app.mainloop()
app.saveConfFile()
