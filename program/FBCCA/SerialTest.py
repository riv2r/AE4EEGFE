import serial

ser = serial.Serial("/dev/ttyS1",9600,timeout=0.5)

ser.open()

ser.write(hex(1))

ser.close()