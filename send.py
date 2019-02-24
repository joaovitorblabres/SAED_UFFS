import serial

ser3 = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)

ser3.writable()
send = "B1\n"
print(send)
while(1):
    ser3.write(send.encode())
    ser3.flushOutput()
    send = ser3.readline().decode()   
    print(send)