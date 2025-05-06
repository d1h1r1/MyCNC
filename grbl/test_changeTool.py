import time
import serial

tool = serial.Serial(port="COM4", baudrate=115200)
move = serial.Serial(port="COM8", baudrate=115200)
unlock_command = "$X\n"
home_command = "$H\n"
set_zero = "S0\n"

loose = "M4 S1000\n"
tighten = "M3 S800\n"
up = "G53 G90 G0 Z-5\n"
down1 = "G53 G90 G0 Z-39\n"
down2 = "G53 G90 G0 Z-40\n"
up1 = "G53 G90 G0 Z-30\n"
coord = ["G53 G90 G0 X-25.731 Y-111.989\n", "G53 G90 G0 X-75.759 Y-114.555\n"]

time.sleep(1)
tool.write(unlock_command.encode())
time.sleep(1)
move.write(unlock_command.encode())
time.sleep(1)

while True:
    move.write(up.encode())  # 抬刀
    tool.write(tighten.encode())  # 紧
    # time.sleep(5)
    move.write(coord[0].encode())

    time.sleep(10)
    move.write(down1.encode())
    time.sleep(5)
    move.write(up.encode())
    time.sleep(5)
    move.write(coord[1].encode())

    tool.write(loose.encode())  # 松
    move.write(down2.encode())  # 还
    time.sleep(3)
    # move.write(up1.encode())
    # move.write(down2.encode())  # 还
    # time.sleep(2)
    move.write(up.encode())
    time.sleep(5)
    tool.write(tighten.encode())  # 紧
    move.write(down1.encode())
    time.sleep(7)
    move.write(up.encode())
    time.sleep(5)
    move.write(coord[0].encode())

    time.sleep(5)
    tool.write(loose.encode())  # 松
    move.write(down2.encode())
    time.sleep(3)
    move.write(up.encode())
    time.sleep(5)


# s = input()
