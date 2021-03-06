import copy, os, sys
import csv
import numpy as np
import time, datetime
import tkinter as tk
import time, codecs
import matplotlib.animation as animation
import matplotlib
import matplotlib.pyplot as plt
import threading
import calibracao
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
from MultiListbox import *
from subprocess import Popen, PIPE

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
	inputs = []
	fileImport = ""
	fileName = ""

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
		self.CheckVars = []
		for i in range(self.sensor):
			self.CheckVars.append(IntVar())
			self.CheckVars[i].set(1)
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
		self.buttonSensors = []
		for i in range(self.sensor):
			self.buttonSensors.append(tk.Checkbutton(self.buttons, text="Sensor "+str(i), variable = self.CheckVars[i], onvalue = 1, offvalue = 0, height = 3, command=replotSensor))
			self.buttonSensors[i].pack(side="top")

		self.logo = tk.Label(self, image = self.logoUFFSPng) #, background='#00693e'
		self.logo.config(image=self.logoUFFSPng)
		self.logo.image = self.logoUFFSPng
		self.logo.grid(row=3, column=0, sticky=W)


		self.mlb = MultiListbox(self, (('DATA_HORA', 20), ('Sensor 0', 8), ('Sensor 1', 8), ('Sensor 2', 8), ('Sensor 3', 8), ('Sensor 4', 8), ('Sensor 5', 8)))
		[self.mlb.insert(END, (input[0], input[1], input[2], input[3], input[4], input[5], input[6])) for input in self.inputs]
		self.mlb.grid(row=2, column=0, pady=5)

	def atualizaMultiList(self):
		self.mlb.delete(0, self.mlb.size())
		[self.mlb.insert(END, (input[0], input[1], input[2], input[3], input[4], input[5], input[6])) for input in self.inputs]

	def importFile(self):
		pack = filedialog.askopenfilename(initialdir = self.filesPath)
		result = "".join(str(x) for x in pack)
		result.replace("()", "")
		if(result != "()" and result != ""):
			self.fileImport = result
			print(self.fileImport)

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

		self.lbInterval = tk.Label(self.toplevel, text = "Intervalo de aferimento de temperatura (em segundos - mínimo de 3):")
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
		global ani
		try:
			self.boards = int(self.Boards.get())
			self.intervalo = int(self.interv.get())
			if(self.intervalo < 3):
				tkMessageBox.showinfo("Menor que 3 segundos", "Menor que 3 segundos, iremos colocar 3 segundos, como mínimo", parent = self.toplevel)
				self.intervalo = 3
			ani.event_source.interval = self.intervalo*1000
			if(self.sensor != int(self.sensors.get())):
					tkMessageBox.showinfo("Reiniciar", "Será necessário reiniciar a aplicação", parent = self.toplevel)
					self.sensor = int(self.sensors.get())
					self.saveConfFile()
					restart_program()
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

f = Figure(figsize=(8,5), dpi=100)
a = f.add_subplot(1, 1, 1)
pCounter = 0
globInter = 0

def restart_program():
	python = sys.executable
	os.execl(python, python, * sys.argv)

dataList = []
colorConf = ['ro', 'go', 'bo', 'yo', 'co', 'ko']
pause = True

def get_time():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))

media = 0
def checkTemp(readed):
	global media
	j = 0
	for b in readed:
		b = float(b)
		if app.CheckVars[j].get() == 1:
			if((b < (media - 25)) or (b > (media + 25))):
				tkMessageBox.showerror("Atencao", "Sensor " + str(j) +" esta com um diferenca grande de temperatura em relacao aos demais")
			elif((b < (media - 10)) or (b > (media + 10))):
				tkMessageBox.showwarning("Atencao","Sensor " + str(j) +" esta com um diferenca pequena de temperatura em relacao aos demais")
		j += 1

def getNumSens():
	global qtdSensoresSelecionados
	qtdSensoresSelecionados = 0
	for sens in range(0, app.sensor):
		if app.CheckVars[sens].get() == 1:
			qtdSensoresSelecionados += 1
			
qtdSensoresSelecionados = 0
def replotSensor():
	global colorConf, globInter, qtdSensoresSelecionados
	qtdSensoresSelecionados = 0
	a.clear()
	for i in range(0, len(app.inputs)):
		k = 0
		for j in range(1, len(app.inputs[i])):
			if app.CheckVars[k].get() == 1:
				a.plot(int(i*globInter), float(app.inputs[i][j]), colorConf[j-1])
				getNumSens()
			if k < app.sensor-1:
				k += 1
	a.set_xlabel('Tempo (s)')
	a.set_ylabel('Temperatura (°C)')
	plt.show()

def plot(dataList, n = 3):
	global pause, globInter, colorConf, media, qtdSensoresSelecionados
	a.clear()
	for line in dataList:
		media = 0
		if line:
			lines = []
			#print(line.split(';'))
			if n == 1:
				lines.append(get_time())
				for i in range(0, len(line)):
					val = int(line[i])*0.31027 + calibracao.sensores[i-1]
					if app.CheckVars[i].get() == 1:
						media += val
					lines.append(val)
			else:
				for i in line.split(';'):
					lines.append(i)
					try:
						media += float(i)
					except:
						pass
			[lines.append(0.0) for i in range(len(lines), 7)]
			if imported == 0:
				with open(app.fileName, 'a') as csvfile:
						spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
						spamwriter.writerow(lines)
						csvfile.close()
				if qtdSensoresSelecionados > 0:
					media /= qtdSensoresSelecionados
				#print(media, qtdSensoresSelecionados)
				checkTemp(lines[1:])
				
			app.inputs.append(lines)
			app.atualizaMultiList()
			try:
				lines = list(map(float, lines[1:-1]))
				Application.tempTotal.append(sum(lines)/len(lines))
				Application.yTotal.append(len(app.inputs)*globInter)
			except Exception as e:
				print(e)

	Application.t = len(app.inputs)
	replotSensor()
	plt.show()

def animate(i = 1):
	global pause, modificationTime, dataList, imported
	#print(app.fileImport)
	if not pause and app.fileImport == "":
		#print("[" + get_time() + "] CHECK")
		Board = "B1"
		fileName = "/home/pi/monitor_temperatura_UFFS/arquivos/temperatura.csv"
		pullData = open(fileName,"r").read()
		lastData = pullData.split('\n')[-2]
		dataList.clear()
		dataList.append(lastData.split(','))
		plot(dataList, 1)
	elif app.fileImport != "" and imported == 0:
		fileName = app.fileImport
		pullData = open(fileName,"r").read()
		dataList = pullData.split('\n')
		imported = 1
		plot(dataList)

imported = 0
root = tk.Tk()
p0 = Popen(['make', 'update'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output0, er0 = p0.communicate(b"")
#print(output0, er0)
if er0.decode() != "":
	tkMessageBox.showinfo("Aviso", "Não foi possível verificar atualizações!\nVocê pode estar desconectado da internet!\nO programa pode estar sendo executado com uma versão desatualizada!", parent = root)
elif output0.decode() != "git pull\nAlready up to date.\n" and output0.decode() != "git pull\n" and output0.decode() != "git pull\nAlready up-to-date.\n":
	tkMessageBox.showinfo("Reiniciar", "Atualização encontrada!\nSerá necessário reiniciar a aplicação!", parent = root)
	restart_program()
app = Application(master=root)
modificationTime = datetime.fromtimestamp(os.path.getmtime("temperature_B1_" + app.strDate + ".csv"))
ani = animation.FuncAnimation(f, animate, interval=app.intervalo*1000)
a.set_xlabel('Tempo (s)')
a.set_ylabel('Temperatura (°C)')
app.mainloop()
app.saveConfFile()
