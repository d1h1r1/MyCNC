#!/usr/bin/env python3
import os
import inkex
import math
from inkex import PathElement
from inkex.paths import Move, Line, ZoneClose, zoneClose, Curve, Arc
from inkex.units import convert_unit


class Gcode:
    def __init__(self, options):
        self.commands = []
        self.servo_status_down = False
        self.servo_up_command = options.servo_up
        self.servo_down_command = options.servo_down
        self.feedrate = options.feedrate
        self.y_invert = options.y_invert
        self.y_offset = options.y_offset
        # Add G-code header
        self.add_header()

    def add_header(self):
        self.commands.extend([
            "G21 ; Set units to millimeters",
            "G90 ; Use absolute coordinates",
            f"{self.servo_up_command} ; Servo_Up",
        ])

    def add_footer(self):
        self.servo_up()
        self.add_fast_move(0, 0)

    def servo_up(self):
        if self.servo_status_down:
            self.commands.append(self.servo_up_command)
            self.servo_status_down = False

    def servo_down(self):
        if not self.servo_status_down:
            self.commands.append(self.servo_down_command)
            self.servo_status_down = True

    def add_fast_move(self, x, y):
        if self.y_invert:
            y = -y
            y = y + self.y_offset
        self.commands.append(f"G0 X{x:.4f} Y{y:.4f}")

    def add_linear_move(self, x, y, feedrate=None):
        if self.y_invert:
            y = -y
            y = y + self.y_offset
        if feedrate is None:
            feedrate = self.feedrate
        self.commands.append(f"G1 X{x:.4f} Y{y:.4f} F{feedrate}")

    def add_dwell(self, seconds):
        self.commands.append(f"G4 P{seconds}")

    def add_arc_move(self, x, y, i, j, clockwise, feedrate=None):
        if self.y_invert:
            y = -y
            y = y + self.y_offset
            j = -j
            # We do NOT offset j because i and j relative measurements from x,y
            clockwise = not clockwise
        if feedrate is None:
            feedrate = self.feedrate
        if clockwise:
            self.commands.append(f"G2 X{x:.4f} Y{y:.4f} I{i:.4f} J{j:.4f} F{feedrate}")
        else:
            self.commands.append(f"G3 X{x:.4f} Y{y:.4f} I{i:.4f} J{j:.4f} F{feedrate}")

    def get_gcode(self):
        return '\n'.join(self.commands)


class PathToGcode(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--feedrate", type=float, default=600.0, help="Feed Rate (mm/min)")
        pars.add_argument("--servo_up", type=str, default="M5", help="Gcode to move cutter up")
        pars.add_argument("--servo_down", type=str, default="M3 S90", help="Gcode to put cutter down")
        pars.add_argument("--mark_zero", type=inkex.Boolean, default=True, help="Mark 0,0")
        pars.add_argument("--directory", type=str, default="", help="Output directory")
        pars.add_argument("--filename", type=str, default="output.gcode", help="Output filename")
        pars.add_argument("--add_numeric_suffix_to_filename", type=inkex.Boolean, default=True,
                          help="Add numeric suffix to filename")
        pars.add_argument("--y_offset", type=float, default=508, help="Apply y = y + offset")
        pars.add_argument("--y_invert", type=inkex.Boolean, default=True, help="Invert the Y axis.")

    def effect(self):
        if not self.svg.selected:
            inkex.errormsg("Please select at least one path.")
            return

        # Initialize G-code generator
        self.gcode = Gcode(self.options)

        feedrate = self.options.feedrate

        if self.options.mark_zero:
            self.gcode.add_fast_move(0, 0)
            self.gcode.servo_down()
            self.gcode.add_dwell(0.5)
            self.gcode.servo_up()

        # Unit conversion: document units to millimeters
        doc_unit = self.svg.unit
        self.scale_factor = convert_unit(1.0, doc_unit, 'mm')
        inkex.utils.debug(f"Scale factor: {self.scale_factor:.4f}")

        # Process selected paths
        for element in self.svg.selection.filter(PathElement):
            path = element.path

            # Apply transformations
            transform = element.composed_transform()
            path = path.transform(transform)

            # Convert path to absolute coordinates
            path = path.to_absolute()
            inkex.utils.debug("processing element")
            inkex.utils.debug(path)

            starting_pos = None
            current_pos = None

            for segment in path:
                if isinstance(segment, Move):
                    x, y = segment.x, segment.y
                    current_pos = x, y
                    x_mm = x * self.scale_factor
                    y_mm = y * self.scale_factor
                    self.gcode.servo_up()
                    self.gcode.add_fast_move(x_mm, y_mm)
                    if starting_pos is None:
                        starting_pos = (x, y)
                elif isinstance(segment, Line):
                    x, y = segment.x, segment.y
                    current_pos = x, y
                    x_mm = x * self.scale_factor
                    y_mm = y * self.scale_factor
                    self.gcode.servo_down()
                    self.gcode.add_linear_move(x_mm, y_mm)
                elif isinstance(segment, ZoneClose) or isinstance(segment, zoneClose):
                    current_pos = starting_pos
                    x_mm = starting_pos[0] * self.scale_factor
                    y_mm = starting_pos[1] * self.scale_factor
                    self.gcode.servo_down()
                    self.gcode.add_linear_move(x_mm, y_mm)
                elif isinstance(segment, Curve):
                    p0 = current_pos
                    p1 = (segment.x2, segment.y2)
                    p2 = (segment.x3, segment.y3)
                    p3 = (segment.x4, segment.y4)
                    self.gcode.servo_down()
                    self.approximate_bezier_with_arcs(p0, p1, p2, p3)
                    current_pos = p3
                else:
                    # For arcs, or all others, we'll issue a warning
                    inkex.errormsg(
                        f"Warning: Segment type '{type(segment).__name__}' is not supported and will be ignored.")

        # Add G-code footer
        self.gcode.add_footer()

        # Handle file output
        directory = self.options.directory or os.path.expanduser("~")
        filename = self.options.filename

        if self.options.add_numeric_suffix_to_filename:
            filename = self.unique_filename(directory, filename)

        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, 'w') as f:
                f.write(self.gcode.get_gcode())
            inkex.utils.debug(f"G-code successfully saved to: {filepath}")
        except IOError as e:
            inkex.errormsg(f"Failed to write to file: {filepath}\n{str(e)}")

    def approximate_bezier_with_arcs(self, p0, p1, p2, p3, tolerance=0.5):
        # Recursive subdivision and arc approximation
        arcs = self.recursive_approximation(p0, p1, p2, p3, tolerance)
        # Generate G-code arcs
        for arc in arcs:
            self.generate_gcode_arc(arc)

    def recursive_approximation(self, p0, p1, p2, p3, tolerance):
        # Calculate circle through start, mid, and end points
        mid_t = 0.5
        mid_point = self.bezier_point(p0, p1, p2, p3, mid_t)
        circle = self.circle_from_three_points(p0, mid_point, p3)
        if circle is None:
            # Subdivide and recurse
            left, right = self.subdivide_bezier(p0, p1, p2, p3)
            return self.recursive_approximation(*left, tolerance) + \
                self.recursive_approximation(*right, tolerance)
        else:
            center, radius = circle
            deviation = self.max_deviation(p0, p1, p2, p3, center, radius)
            if deviation <= tolerance:
                # Accept the arc approximation
                start_angle = math.atan2(p0[1] - center[1], p0[0] - center[0])
                end_angle = math.atan2(p3[1] - center[1], p3[0] - center[0])
                return [(center, radius, start_angle, end_angle, p0, p3)]
            else:
                # Subdivide and recurse
                left, right = self.subdivide_bezier(p0, p1, p2, p3)
                return self.recursive_approximation(*left, tolerance) + \
                    self.recursive_approximation(*right, tolerance)

    def bezier_point(self, p0, p1, p2, p3, t):
        # Cubic Bezier point calculation
        mt = 1 - t
        x = mt ** 3 * p0[0] + 3 * mt ** 2 * t * p1[0] + 3 * mt * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = mt ** 3 * p0[1] + 3 * mt ** 2 * t * p1[1] + 3 * mt * t ** 2 * p2[1] + t ** 3 * p3[1]
        return (x, y)

    def circle_from_three_points(self, p1, p2, p3):
        # Calculate circle center and radius through three points
        temp = p2[0] ** 2 + p2[1] ** 2
        bc = (p1[0] ** 2 + p1[1] ** 2 - temp) / 2.0
        cd = (temp - p3[0] ** 2 - p3[1] ** 2) / 2.0
        det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])
        if abs(det) < 1e-10:
            return None
        cx = (bc * (p2[1] - p3[1]) - cd * (p1[1] - p2[1])) / det
        cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det
        radius = math.hypot(p2[0] - cx, p2[1] - cy)
        return ((cx, cy), radius)

    def max_deviation(self, p0, p1, p2, p3, center, radius):
        # Calculate maximum deviation between Bezier and arc
        deviations = []
        for t in [0.25, 0.5, 0.75]:
            bez_pt = self.bezier_point(p0, p1, p2, p3, t)
            angle = math.atan2(bez_pt[1] - center[1], bez_pt[0] - center[0])
            arc_pt = (
                center[0] + radius * math.cos(angle),
                center[1] + radius * math.sin(angle)
            )
            deviations.append(math.hypot(bez_pt[0] - arc_pt[0], bez_pt[1] - arc_pt[1]))
        return max(deviations)

    def subdivide_bezier(self, p0, p1, p2, p3):
        # Subdivide cubic Bezier curve into two halves
        p01 = self.mid_point(p0, p1)
        p12 = self.mid_point(p1, p2)
        p23 = self.mid_point(p2, p3)
        p012 = self.mid_point(p01, p12)
        p123 = self.mid_point(p12, p23)
        p0123 = self.mid_point(p012, p123)
        left = (p0, p01, p012, p0123)
        right = (p0123, p123, p23, p3)
        return left, right

    def mid_point(self, p1, p2):
        # Calculate midpoint between two points
        return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)

    def generate_gcode_arc(self, arc):
        center, radius, start_angle, end_angle, p_start, p_end = arc
        # Determine arc direction
        delta_angle = (end_angle - start_angle) % (2 * math.pi)
        clockwise = delta_angle > math.pi
        # Calculate I and J offsets
        i = center[0] - p_start[0]
        j = center[1] - p_start[1]
        # Convert coordinates to mm
        x_end_mm = p_end[0] * self.scale_factor
        y_end_mm = p_end[1] * self.scale_factor
        i_mm = i * self.scale_factor
        j_mm = j * self.scale_factor
        # Use gcode instance to add arc move
        self.gcode.add_arc_move(x_end_mm, y_end_mm, i_mm, j_mm, clockwise)

    def unique_filename(self, directory, filename):
        base, ext = os.path.splitext(filename)
        i = 1
        unique_filename = filename
        while os.path.exists(os.path.join(directory, unique_filename)):
            unique_filename = f"{base}_{i}{ext}"
            i += 1
        return unique_filename


if __name__ == '__main__':
    PathToGcode().run()
