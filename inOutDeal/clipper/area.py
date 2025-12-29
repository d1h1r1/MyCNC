import pyclipper

polygon = [(0, 0), (4, 0), (4, 3), (0, 3)]
print("面积:", pyclipper.Area(polygon))
