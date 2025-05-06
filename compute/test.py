def calculate_chk(device, cmd, status, data):
    chk = 0x00
    for byte in device:
        chk ^= byte  # 继续异或数据数组中的每个字节
    for byte in cmd:
        chk ^= byte  # 继续异或数据数组中的每个字节
    for byte in status:
        chk ^= byte  # 继续异或数据数组中的每个字节
    for byte in data:
        chk ^= byte  # 继续异或数据数组中的每个字节
    return chk


# 示例数据
device = [0x00, 0x00]
cmd = [0x0C, 0x06]
status = [0x00]
data = [0x52, 0x08]

chk_value = calculate_chk(device, cmd, status, data)
print(f"校验位 CHK: {chk_value:#04x}")  # 输出十六进制格式


# 读卡
# AA BB 0D 00 00 00 08 06 60 01 FF FF FF FF FF FF 6F
# AA BB 07 00 00 00 0C 06 52 08 50


# 写卡
# AA BB 1D 00 00 00 09 06 60 01 FF FF FF FF FF FF 11 22 33 44 55 66 77 88 99 00 AA 00  BB CC DD EE FF 6E
# AA BB 0B 00 00 00 0D 06 52 08 11 22 33 44 15