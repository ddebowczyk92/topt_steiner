from Tkinter import Canvas, Tk, Frame, Button, RAISED, TOP, StringVar, Label, RIGHT, RIDGE, LEFT, BOTTOM
from steiner import TOPTGraph, SteinerTree
import math
import itertools
import sys
import Queue
import threading
import time
import re

import random as rand


def enum(**enums):
    return type('Enum', (), enums)


GuiConfig = enum(GUI_WIDTH=700,
                 GUI_HEIGHT=500,
                 POINT_RADIUS=10,
                 POINT_OUTLINE=3
                 )


class Point:
    """Point Class for Steiner.py
    Contains position in x and y values with degree of edges representative of the length of
    the list of edges relative to the MST
    """

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = GuiConfig.POINT_RADIUS
        self.outline = '#34495e'
        self.fill = '#1abc9c'
        self.edges = []

    def update(self, edge):
        self.edges.append(edge)

    def reset(self):
        self.edges = []


class OLTPoint(Point):
    def __init__(self, id, x, y):
        Point.__init__(self, id, x, y)


class ONUPoint(Point):
    def __init__(self, id, x, y):
        Point.__init__(self, id, x, y)
        self.outline = '#2980b9'
        self.fill = '#8e44ad'


class TerminalPoint(Point):
    def __init__(self, id, x, y):
        Point.__init__(self, id, x, y)
        self.outline = '#c0392b'
        self.fill = '#34495e'
        self.radius = 5


class GuiLine:
    """Line Class for Steiner.py
    Contains the two end points as well as the weight of the line.
    Supports determining the first or last point as well as the other given one.
    """

    def __init__(self, p1, p2, w):
        self.points = []
        self.points.append(p1)
        self.points.append(p2)
        self.w = w

    def getOther(self, pt):
        if pt == self.points[0].get():
            return self.points[1]
        elif pt == self.points[1].get():
            return self.points[0]
        else:
            print "This is an Error. The line does not contain points that make sense."

    def getFirst(self):
        return self.points[0]

    def getLast(self):
        return self.points[1]


class TOPTGui(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        # master = Canvas(self)
        self.master.resizable(width=False, height=False)
        self.canvas = Canvas(self.master, width=GuiConfig.GUI_WIDTH,
                             height=GuiConfig.GUI_HEIGHT, bd=2, relief=RIDGE, bg='#2c3e50')
        self.canvas.bind("<Button-1>", self.add_mouse_point)

        self.but_frame = Frame(self.master)
        self.clear_button = Button(self.but_frame, text="Clear", command=self.clear_canvas)
        self.clear_button.configure(width=9)
        self.clear_button.pack(side=TOP)

        self.compute_button = Button(self.but_frame, text="Compute", command=self.start_computing)
        self.compute_button.configure(width=9)
        self.compute_button.pack()

        self.canvas.pack(side=LEFT, expand=0)
        self.but_frame.pack(side=RIGHT, expand=0)

        self.points = {}
        self.edges = []
        self.id_atomic = itertools.count()
        self.olt_added = False
        self.olt_point_id = None

        self.queue = Queue.Queue()
        self.lock_object = object();

    def __add_point(self, x, y):
        point = None
        id = str(self.id_atomic.next())
        if (self.olt_added):
            point = ONUPoint(id, x, y)
        else:
            point = OLTPoint(id, x, y)
            self.olt_added = True
            self.olt_point_id = id

        self.canvas.create_oval(x - point.radius, y - point.radius, x + point.radius,
                                y + point.radius, outline=point.outline, fill=point.fill, width=3)
        self.canvas.bind("<Button-1>", self.add_mouse_point)
        self.points[id] = point

    def draw_point(self, point):
        self.canvas.create_oval(point.x - point.radius, point.y - point.radius, point.x + point.radius,
                                point.y + point.radius, outline=point.outline, fill=point.fill, width=3)

        self.canvas.bind("<Button-1>", self.add_mouse_point)

    def add_mouse_point(self, event):
        addpt = True
        if self.points == {}:
            if (event.x < GuiConfig.POINT_RADIUS) and (event.x >= GuiConfig.GUI_WIDTH) \
                    and (event.y < GuiConfig.POINT_RADIUS) and (event.y >= GuiConfig.GUI_HEIGHT):
                addpt = False
        else:
            for id, pt in self.points.items():
                dist = math.sqrt(pow((event.x - pt.x), 2) + pow((event.y - pt.y), 2))
                if dist < 2 * (GuiConfig.POINT_RADIUS + GuiConfig.POINT_OUTLINE):
                    addpt = False
                if (event.x < GuiConfig.POINT_RADIUS) and (event.x >= GuiConfig.GUI_WIDTH) \
                        and (event.y < GuiConfig.POINT_RADIUS) and (event.y >= GuiConfig.GUI_HEIGHT):
                    addpt = False
        if addpt == True:
            self.__add_point(event.x, event.y)

    def clear_canvas(self):
        self.points = {}
        self.edges = []
        self.id_atomic = itertools.count()
        self.olt_added = False
        self.olt_point_id = None

        self.canvas.delete('all')

    def quit(self):
        sys.exit()

    def start_computing(self):
        self.thread1 = threading.Thread(target=self.worker_thread)
        self.thread1.start()
        root.after(5, self.check_progress)

    def worker_thread(self):
        self.queue.put('Started computing...')
        time.sleep(10)

        self.queue.put(self.lock_object)

    def check_progress(self):
        try:
            msg = self.queue.get_nowait()

            if msg is not self.lock_object:

                root.after(1, self.check_progress)
            else:

                pass
        except Queue.Empty:
            root.after(5, self.check_progress)

    def start_computing(self):
        graph = TOPTGraph()
        olt_point = self.points[self.olt_point_id]
        graph.add_node_with_position(olt_point.id, olt_point.x, olt_point.y)
        for id, point in self.points.items():
            if (id != olt_point.id):
                graph.add_node_with_position(id, point.x, point.y)
                graph.add_euclidian_edge(olt_point.id, id)
        steiner = SteinerTree()
        solution, cost = steiner.find_steiner_tree(graph)
        self.add_terminal_points(solution)
        self.draw_edges(solution.edges())

    def add_terminal_points(self, solution):
        for node_id in solution.nodes():
            if re.search('F\(', node_id):
                node = solution.node[node_id]
                position = node['pos']
                terminal_point = TerminalPoint(node_id, position[0], position[1])
                self.points[node_id] = terminal_point
                self.draw_point(terminal_point)

    def draw_edges(self, edges):
        for edge in edges:
            point_1 = self.points[edge[0]]
            point_2 = self.points[edge[1]]
            self.canvas.create_line(point_1.x, point_1.y,
                                    point_2.x, point_2.y, width=2)


if __name__ == "__main__":
    root = Tk()
    gui = TOPTGui(root)
    root.mainloop()
