import json
import time
import serial
ser = serial.Serial(port="COM23", baudrate=115200)
unlock_command = "$X\n"
home_command = "$H\n"
set_zero = "S0\n"
help_command = "$$\n"
state_command = "?\n"

z_probe_command = ["G90G01X-153.339Y-77.775F1000\n", "G91G38.2Z-50F200\n", "G0Z2\n", "G38.2Z-3F30\n", "G90G01Z-3F1000\n"]
lx_probe_command = ["G90G01X-267.171Y-77.775F1000\n", 0, "G91G38.2X50F200\n", "G0X-2\n", "G38.2X3F30\n", "G0X-2F1000\n", "G90G01Z-3F1000\n"]
rx_probe_command = ["G90G01X-39.506Y-77.775F1000\n", 0, "G91G38.2X-50F200\n", "G0X2\n", "G38.2X-3F30\n", "G0X2F1000\n", "G90G01Z-3F1000\n"]
ony_probe_command = ["G90G01X-153.339Y-28.717F1000\n", 0, "G91G38.2Y-50F200\n", "G0Y2\n", "G38.2Y-3F30\n", "G0Y2F1000\n", "G90G01Z-3F1000\n"]
undery_probe_command = ["G90G01X-153.339Y-126.833F1000\n", 0, "G91G38.2Y50F200\n", "G0Y-2\n", "G38.2Y3F30\n", "G0Y-2F1000\n", "G90G01Z-3F1000\n"]

time.sleep(3)

data = ser.read_all()
print(data.decode(), "==========")

ser.write(home_command.encode())
time.sleep(0.05)
data = ser.read_all()
print(data.decode(), "==========")
s = input()

ser.write(state_command.encode())
time.sleep(0.05)
data = ser.read_all()
print(data.decode(), "==========")
s = input()


for i in z_probe_command:
    ser.write(i.encode())
    time.sleep(0.05)
    data = ser.read_all()
    print(data.decode(), "==========")
s = input()
data = ser.read_all()
print(data.decode(), "==========")
all_str = data.decode()
start_index = all_str.rfind("PRB") + 4
end_index = all_str.rfind("]") - 2
txt = "[" + all_str[start_index: end_index] + "]"
z_coord = json.loads(txt)[2]
print(z_coord)

for i in lx_probe_command:
    if i == 0:
        z_move = f"G90G01Z{z_coord - 1}F1000\n"
        ser.write(z_move.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
    else:
        ser.write(i.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
s = input()
data = ser.read_all()
print(data.decode(), "==========")
all_str = data.decode()
start_index = all_str.rfind("PRB") + 4
end_index = all_str.rfind("]") - 2
txt = "[" + all_str[start_index: end_index] + "]"
lx_coord = json.loads(txt)[0]
print(lx_coord)

for i in rx_probe_command:
    if i == 0:
        z_move = f"G90G01Z{z_coord - 1}F1000\n"
        ser.write(z_move.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
    else:
        ser.write(i.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
s = input()
data = ser.read_all()
print(data.decode(), "==========")
all_str = data.decode()
start_index = all_str.rfind("PRB") + 4
end_index = all_str.rfind("]") - 2
txt = "[" + all_str[start_index: end_index] + "]"
rx_coord = json.loads(txt)[0]
print(rx_coord)

for i in ony_probe_command:
    if i == 0:
        z_move = f"G90G01Z{z_coord - 1}F1000\n"
        ser.write(z_move.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
    else:
        ser.write(i.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
s = input()
data = ser.read_all()
print(data.decode(), "==========")
all_str = data.decode()
start_index = all_str.rfind("PRB") + 4
end_index = all_str.rfind("]") - 2
txt = "[" + all_str[start_index: end_index] + "]"
ony_coord = json.loads(txt)[1]
print(ony_coord)

for i in undery_probe_command:
    if i == 0:
        z_move = f"G90G01Z{z_coord - 1}F1000\n"
        ser.write(z_move.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
    else:
        ser.write(i.encode())
        time.sleep(0.05)
        data = ser.read_all()
        print(data.decode(), "==========")
s = input()
data = ser.read_all()
print(data.decode(), "==========")
all_str = data.decode()
start_index = all_str.rfind("PRB") + 4
end_index = all_str.rfind("]") - 2
txt = "[" + all_str[start_index: end_index] + "]"
undery_coord = json.loads(txt)[1]
print(undery_coord)

center_coord = [(lx_coord + rx_coord) * 0.5, (ony_coord + undery_coord) * 0.5, z_coord]
print(center_coord)

s = input()
xycenter_move = f"G90G01X{center_coord[0]}Y{center_coord[1]}F1000\n"
ser.write(xycenter_move.encode())
time.sleep(0.05)
data = ser.read_all()
print(data.decode(), "==========")

s = input()
zcenter_move = f"G90G01Z{center_coord[2]}F200\n"
ser.write(zcenter_move.encode())
time.sleep(0.05)
data = ser.read_all()
print(data.decode(), "==========")

# ser.write(help_command.encode())
# time.sleep(0.05)
# data = ser.read_all()
# print(data.decode(), "==========")

# ser.write(state_command.encode())
# time.sleep(0.05)
# data = ser.read_all()
# print(data.decode())
# print(data.decode(), "==========")
