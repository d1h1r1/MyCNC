import threading
import time
import serial

lock = threading.Lock()

move = serial.Serial(port="COM10", baudrate=115200)
unlock_command = "$X\n"
set_zero = "S0\n"

time.sleep(1)
move.write(unlock_command.encode())
time.sleep(1)

# 大电流风扇
fan1_open = "$FB1\n"
fan1_close = "$FB0\n"
fan2_open = "$FC1\n"
fan2_close = "$FC0\n"
fan3_open = "$FD1\n"
fan3_close = "$FD0\n"

# 小电流风扇
fan4_open = "$FA1\n"
fan4_close = "$FA0\n"

# 电磁阀
ele1_open = "$FG1\n"
ele1_close = "$FG0\n"
ele2_open = "$FH1\n"
ele2_close = "$FH0\n"
ele3_open = "$FK1\n"
ele3_close = "$FK0\n"


def bigFan():
    with lock:
        while True:
            move.write(fan1_open.encode())
            print("1开")
            time.sleep(30)
            move.write(fan1_close.encode())
            move.write(fan2_open.encode())
            time.sleep(30)
            move.write(fan2_close.encode())
            move.write(fan3_open.encode())
            time.sleep(30)
            move.write(fan3_close.encode())


def smallFan():
    with lock:
        while True:
            move.write(fan4_open.encode())
            time.sleep(30)
            move.write(fan4_close.encode())
            time.sleep(3)


def ele():
    with lock:
        while True:
            move.write(ele1_open.encode())
            move.write(ele2_open.encode())
            move.write(ele3_open.encode())
            time.sleep(3)
            move.write(ele1_close.encode())
            move.write(ele2_close.encode())
            move.write(ele3_close.encode())
            time.sleep(3)


threading.Thread(target=bigFan, args=()).start()
threading.Thread(target=smallFan, args=()).start()
threading.Thread(target=ele, args=()).start()
