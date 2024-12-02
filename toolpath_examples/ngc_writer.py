# very simple G-code writer.
# Anders Wallin 2012

clearance_height = 0
feed_height = 0
feed = 200
plunge_feed = 0
metric = True

f = open("../file/test.nc", "w")

print_flag = False

def line_to(x, y, z):
    command = "G1 X% 8.6f Y% 8.6f Z% 8.6f F%.0f" % (x, y, z, feed)
    f.write(command + "\n")
    if print_flag:
        print(command)


def xy_line_to(x, y):
    command = "G1 X% 8.4f Y% 8.4f " % (x, y)
    f.write(command + "\n")
    if print_flag:
        print(command)


# (endpoint, radius, center, cw?)
def xy_arc_to(x, y, r, cx, cy, cw):
    if cw:
        command = "G2 X% 8.5f Y% 8.5f R% 8.5f" % (x, y, r)
        f.write(command + "\n")
        if print_flag:
            print(command)
    else:
        command = "G3 X% 8.5f Y% 8.5f R% 8.5f" % (x, y, r)
        f.write(command + "\n")
        if print_flag:
            print(command)
    # FIXME: optional IJK format arcs


def xy_rapid_to(x, y):
    command = "G0 X% 8.4f Y% 8.4f " % (x, y)
    f.write(command + "\n")
    if print_flag:
        print(command)


def pen_up():
    command = "G0Z% 8.4f " % clearance_height
    f.write(command + "\n")
    if print_flag:
        print(command)


"""
def pen_down():
    print("G0Z% 8.4f" % (feed_height))
    plunge(0)
"""


def pen_down(z=0):
    command = "G0Z% 8.4f" % feed_height
    f.write(command + "\n")
    if print_flag:
        print(command)
    plunge(z)


def plunge(z):
    command = "G1 Z% 8.4f F% 8.0f" % (z, plunge_feed)
    f.write(command + "\n")
    if print_flag:
        print(command)


def preamble():
    if metric:
        command = "G21 F% 8.0f" % feed
        f.write(command + "\n")
        if print_flag:
            print(command)
    else:
        command = "G20 F% 8.0f" % feed
        f.write(command + "\n")
        if print_flag:
            print(command)

    # print("G64 P0.001")  # linuxcnc blend mode
    pen_up()
    command = "G0 X0 Y0"  # this might not be a good idea!?
    f.write(command + "\n")
    if print_flag:
        print(command)


def postamble():
    pen_up()
    command = "M30"  # end of program
    f.write(command + "\n")
    if print_flag:
        print(command)


def comment(s=""):
    command = "( " + s + " )"
    f.write(command + "\n")
    if print_flag:
        print(command)


if __name__ == "__main__":
    if print_flag:
        print("Nothing to see here.")
