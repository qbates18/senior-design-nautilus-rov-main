# print("Try5: analoggaugewidget.py")
import sys
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class AnalogGaugeWidget(QWidget):
    def __init__(self):
        super(AnalogGaugeWidget, self).__init__()
        self.use_timer_event = False
        self.value_min = 0
        self.value_max = 1000
        self.value = self.value_min
        self.value_offset = 0
        self.value_needle_snapzone = 0.05
        self.last_value = 0
        self.set_NeedleColor(50, 50, 50, 255)
        self.scale_angle_start_value = 135
        self.scale_angle_size = 270
        self.angle_offset = 0
        self.enable_Needle_Polygon = True
        self.set_enable_barGraph(True)
        self.value_needle = QObject


    def set_enable_barGraph(self, enable = True):
        self.enable_barGraph = enable

        if not self.use_timer_event:
            self.update()

    def draw_needle(self):
        painter = QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.value - self.value_offset - self.value_min) * self.scale_angle_size /
                        (self.value_max - self.value_min)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])

    def set_NeedleColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColor = QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

    def set_MinValue(self, min):
        if self.value < min:
            self.value = min
        if min >= self.value_max:
            self.value_min = self.value_max - 1
        else:
            self.value_min = min

        if not self.use_timer_event:
            self.update()

    def set_MaxValue(self, max):
        if self.value > max:
            self.value = max
        if max <= self.value_min:
            self.value_max = self.value_min + 1
        else:
            self.value_max = max

        if not self.use_timer_event:
            self.update()

    def paintEvent(self, event):

        # draw needle 1
        if self.enable_Needle_Polygon:
            self.draw_needle()
    
    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght):
        polygon_pie = QPolygonF()
        # start = self.scale_angle_start_value
        # start = 0
        # lenght = self.scale_angle_size
        # lenght = 180
        # inner_raduis = self.width()/4
        # print(start)
        n = 360     # angle steps size for full circle
        # changing n value will causes drawing issues
        w = 360 / n   # angle per step
        # create outer circle line from "start"-angle to "start + lenght"-angle
        x = 0
        y = 0

        # todo enable/disable bar graf here
        if not self.enable_barGraph:
            # float_value = ((lenght / (self.value_max - self.value_min)) * (self.value - self.value_min))
            lenght = int(round((lenght / (self.value_max - self.value_min)) * (self.value - self.value_min)))
            # print("f: %s, l: %s" %(float_value, lenght))
            pass

        # mymax = 0

        for i in range(lenght+1):                                              # add the points of polygon
            t = w * i + start - self.angle_offset
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))
        # create inner circle line from "start + lenght"-angle to "start"-angle
        for i in range(lenght+1):                                              # add the points of polygon
            # print("2 " + str(i))
            t = w * (lenght - i) + start - self.angle_offset
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))

        # close outer line
        polygon_pie.append(QPointF(x, y))
        return polygon_pie


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gauge = AnalogGaugeWidget()
    gauge.show()
    sys.exit(app.exec_())
