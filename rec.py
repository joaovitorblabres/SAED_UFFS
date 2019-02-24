import serial

ser3 = serial.Serial(
    port='/dev/tnt1',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS
)

ser3.readable()
#send = "70.0;70.5;70.5;70.0;70.5;70.5\n"
while(1):
    reading = ser3.readline().decode()
    print(reading)
