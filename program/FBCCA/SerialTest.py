import serial
 
# 连接串口
serial = serial.Serial('COM7',115200,timeout=2)

if serial.isOpen():

    print ('串口已打开')
    '''
    ASCII码对应指令
    49 50 51 52
    1  2  3  4
    前 左 右 后
    '''

    data = (chr(50)+'\r\n').encode()# 发送的数据
    serial.write(data)# 串口写数据
 
    while True:
        data = serial.read(20)# 串口读20位数据
        if data != b'':
            break
    print(data)
    
else:
    print ('串口未打开')
 
 
 
# 关闭串口
serial.close()
 
if serial.isOpen():
    print ('串口未关闭')
else:
    print ('串口已关闭')
