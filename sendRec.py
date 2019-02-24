import serial
import serial.rs485
import time, codecs

ser3 = serial.Serial(
    port='/dev/serial0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)
#ser3.open()
#print(serial.XOFF)
while(1):
    reading = ser3.readline()
    #print(reading)
    leng = len(reading)
    saida = ''
    if(leng > 4):
        #print(reading.decode())
        for i in range(0, leng-6, 4):
            #print(i+2)
            saida += reading.decode()[i+2]
            saida += reading.decode()[i+3]
        print(codecs.decode(saida, "hex"))
    ser3.flushInput()
    #reading = ser3.readline()
    #print(reading)

 #   print(send[i].encode())
 #   if(i < len(send)-1):
 #       i += 1
    ser3.close()
    time.sleep(1)
    ser3.open()