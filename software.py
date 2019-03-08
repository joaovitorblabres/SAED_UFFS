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
from tkinter import BOTH, END, LEFT, font, N, NE, NW, W, S
from tkinter import ttk, filedialog, StringVar
from tkinter import messagebox as tkMessageBox
from numpy.linalg import inv
from scipy.optimize import curve_fit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from PIL import ImageTk, Image
from datetime import datetime
from multiprocessing import Process

ser3 = serial.Serial(
    port='/dev/serial0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)
# ser.isOpen()
## TESTES COM VIRTUALIZACAO
#ser2 = serial.Serial(
#    port='/dev/tnt0',
#    baudrate=9600,
#    parity=serial.PARITY_ODD,
#    stopbits=serial.STOPBITS_TWO,
#    bytesize=serial.EIGHTBITS
#)

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

    def receive():
        while(1):
            leng = 0
            try:
                ser3.flushInput()
                reading = ser3.readline()
                leng = len(reading)
                saida = ''
            except:
                print("Erro de leitura, confira a conexão")
                time.sleep(2)
            if(leng > 8*4*5):
                try:
                    readed2str = bytearray(reading)
                    #reading.replace('\xad', '')
                    try:
                        readed2str[:1].decode()
                    except:
                        del readed2str[0]
                    for i in range(0, leng-6, 4):
                        saida += readed2str.decode()[i+2]
                        saida += readed2str.decode()[i+3]
                    readed = codecs.decode(saida, "hex")
                    readed = readed.decode("utf-8").split("=")
                    readed[1] += '0'
                    complete = []
                    fileName = "temperature_" + readed[0] + "_" + Application.strDate + ".csv"
                    media = 0
                    tSensores = Application.sensor
                    for i in range(0, tSensores):
                        val = float(readed[1].split(';')[i]) - 11
                        complete.append(val)
                        media += val
                    media /= tSensores
                    j = 1
                    print(complete[:Application.sensor])
                    for b in complete:
                        if((b < (media - 10)) or (b > (media + 10))):
                            tkMessageBox.showerror("Atencao", "Sensor " + str(j) +" esta com um diferenca grande de temperatura em relacao aos demais")
                        elif((b < (media - 5)) or (b > (media + 5))):
                            tkMessageBox.showwarning("Atencao","Sensor " + str(j) +" esta com um diferenca pequena de temperatura em relacao aos demais")
                        j += 1
                    with open(fileName, 'a') as csvfile:
                        spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                        spamwriter.writerow(complete[:Application.sensor])
                        csvfile.close()
                    time.sleep(Application.intervalo-2)                    
                except:
                    print("Erro de conversão, aguarde a próxima tentativa")
                
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

    def confs(self):
        self.master.title("Software SAED")
        self.master.maxsize(1000, 600)
        self.master.minsize(1000, 600)

    def create_widgets(self):
        self.tempera.start()
        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, anchor = S, fill=tk.BOTH)

        # USAR FRAME
#        self.toolbar = NavigationToolbar2QT(self.canvas, self)
#        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.image = Image.open("files/conf.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.confPng = ImageTk.PhotoImage(self.image)
        self.image = Image.open("files/exit.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.exitPng = ImageTk.PhotoImage(self.image)
        self.image = Image.open("files/upload.png")
        self.image = self.image.resize((32, 32), Image.ANTIALIAS)
        self.uplPng = ImageTk.PhotoImage(self.image)

        self.confs = tk.Button(self, command=self.configuracoes)
        self.confs.config(image=self.confPng)
        self.confs.image = self.confPng

        self.quit = tk.Button(self, command=root.destroy)
        self.quit.config(image=self.exitPng)
        self.quit.image = self.exitPng
        self.quit.pack(anchor=NE, side="right")
        self.confs.pack(anchor=NE, side="right")

        self.upload = tk.Button(self, command=self.importFile)
        self.upload.config(image=self.uplPng)
        self.upload.image = self.uplPng
        self.upload.pack(anchor=NE, side="right")

        #self.getTemperature = tk.Button(self, font = "Verdana 10 bold")
        #self.getTemperature["text"] = "Adquirir temperatura"
        #self.getTemperature["command"] = self.getTemp
        #self.getTemperature.pack(side="bottom", ipadx=10, ipady=5)

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

        #self.lbQtd = tk.Label(self.toplevel, text = "Quantidade de leituras a serem realizadas:")
        #self.lbQtd.pack(expand=1, pady=2)
        #self.leituras = tk.Entry(self.toplevel, text = self.qtdLeituras)
        #self.leituras.delete(0, END)
        #self.leituras.insert(0, self.qtdLeituras)
        #self.leituras.pack(expand=1, pady=2)

        self.lbPath = tk.Label(self.toplevel, text = "Local para salvar os dados:")
        self.lbPath.pack(expand=1, pady=2)
        self.paths = tk.Label(self.toplevel, text = self.filesPath)
        self.paths.pack(expand=1, pady=2)
        self.pathB = tk.Button(self.toplevel, text = "Selecionar", command=self.changePath)
        self.pathB.pack(expand=1, pady=2)

       # self.lbTemp = tk.Label(self.toplevel, text = "Tipo de graus:")
        #self.lbTemp.pack(expand=1, pady=2)
        #self.tempType = tk.Radiobutton(self.toplevel, text="Celsius", variable=self.typeTemp, value="0")
        #self.tempType.pack(expand=1, pady=2)
        #self.tempType = tk.Radiobutton(self.toplevel, text="Fahrenheit", variable=self.typeTemp, value="1")
        #self.tempType.pack(expand=1, pady=2)

        #Fahrenheit = 9.0/5.0 * Celsius + 32

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
            self.qtdLeituras = int(self.leituras.get())
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

    #def temps(self):
    #    ABOUT_TEXT = "ADQUIRINDO TEMPERATURA DOS SENSORES"
    #    toplevel = tk.Toplevel(master=self.master)
    #    self.label1 = tk.Label(toplevel, text=ABOUT_TEXT, height=0, width=50)
    #    self.label1.pack()
    #    for kl in range(1, self.boards+1):
    #        x = "B" + str(kl) + "|" + "\n"
    #        Board = "B" + str(kl)
    #        fileName = "temperature_" + Board + "_" + self.strDate + ".csv"
    #        med = self.getFile(fileName)
    #        media = map(float, med[2:])
    #        result = 0
    #        sens = []
    #        for b in media:
    #            result += b
    #            sens.append(b)
    #        result /= self.sensor
    #        j = 1
    #        for b in sens:
    #            if((b < (result - 10)) or (b > (result + 10))):
    #                tkMessageBox.showerror("Atencao", "Sensor " + str(j) +" esta com um diferenca grande de temperatura em relacao aos demais")
    #            elif((b < (result - 3)) or (b > (result + 3))):
    #                tkMessageBox.showwarning("Atencao","Sensor " + str(j) +" esta com um diferenca pequena de temperatura em relacao aos demais")
    #            j += 1
    #    toplevel.destroy()

    #def getTemp(self):
    #    temp = threading.Thread(target=self.controleLeituras)
    #    temp.start()
    #    temp.join(timeout=self.intervalo)

    #def controleLeituras(self):
    #    i = 0
    #    while(i < self.qtdLeituras):
    #        temp = threading.Thread(target=self.temps)
    #        temp.start()
    #        temp.join(timeout=self.intervalo)
    #        time.sleep(self.intervalo)
    #        i += 1
    #    return

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


f = Figure(figsize=(6,4), dpi=100)
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

def MountFunE(coef):
	func = ""
	func += "%f*exp(%f*x)"%(exp(coef[1]), coef[0])
	return func

def mountFunc(a, c, d):
    return "{:.4f}*exp({:.4f}*x)+{:.4f}".format(a, c, d)

def ajustePolinomialE(Y, A):
    lnY = zeros(shape=(len(Y)))
    for i in range(0, len(Y)):
        lnY[i] = log(Y[i])
        At = A.transpose()
    return dot(inv(dot(At, A)), dot(At, lnY))

def exponencial2(X, Y):
    global pCounter
    A = zeros(shape=(len(X), 2))
    for i in range (0, len(X)):
        expo = 1;
        for j in range (0, 2):
            A[i][j] = X[i]**expo
            expo -= 1

    function2 = ajustePolinomialE(Y, A)
    funcao2 = MountFunE(function2)
    pCounter += 1
    if((pCounter % 10) == 0):
        print("Y = %s"%(funcao2))
    f2 = lambda x : eval(funcao2)
    a.set_xlim(X[0]-10, X[len(X)-1]+10)
    a.set_ylim(Y[len(Y)-1]-10, Y[0]+10)
    a.set_title(funcao2, fontsize=11)
    a.plot([x for x in frange(int(X[0])-10, int(X[len(X)-1])+10)], [f2(x) for x in frange(int(X[0])-10, int(X[len(X)-1])+10)], label="Fitted Curve")
    plt.show()

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

def animate(i = 1, name = ""):
    i = 1
    Board = "B1"
    if(name == ""):
        fileName = "temperature_" + Board + "_" + Application.strDate + ".csv"
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
