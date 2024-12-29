from math import sqrt
import debug_console as debug
class ScriptorCanvas():
    def __init__(self,canvas):
        self.canvas = canvas
        self.canvas.bind("<Button-1>", self.on_click)
    def on_click(self,event):
        pass
    def update(self):
        self.clear()
        self.draw()
    def clear(self,tag="grid",del_all_except_tag=True):
        if not del_all_except_tag:
            self.canvas.delete(tag)
        else:
            for item in self.canvas.find_all():
                if tag not in self.canvas.gettags(item):
                    self.canvas.delete(item)
    def draw(self):
        pass

class EditorCanvas(ScriptorCanvas):
    def __init__(self,canvas):
        super().__init__(canvas)
        self.letter = Letter()
        self.letter.segments.append(Segment())
        self.mode = "normal" #normal/selection_simple/selection_multiple
        self.selection_type = None #node/None/connector
        self.num_selected = 0
    def on_click(self,event):
        x,y = event.x-350, event.y-300
        selected = False
        for node in self.letter.segments[0].nodes:
            dist = sqrt((x-node.x)**2+(y-node.y)**2)
            if dist <= node.size + 3:
                if self.selection_type == "connector":
                    self.deselect_all_connectors()
                    self.mode = "normal"
                    self.selection_type = None
                    self.num_selected = 0
                if node.selected:
                    node.deselect()
                    self.num_selected -= 1
                    self.mode = "selection_simple" if self.num_selected == 1 else "normal" if self.num_selected == 0 else self.mode
                    if self.mode == "normal":
                        self.selection_type = None
                else:
                    node.select()
                    self.mode = "selection_simple" if self.mode == "normal" else "selection_multiple"
                    if self.mode == "selection_simple":
                        self.selection_type = "node"
                    self.num_selected += 1
                selected = True
        if not selected:
            mode = self.mode
            if mode != "normal" and self.selection_type == "node":
                self.deselect_all_nodes()
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
            for i in range(0,len(self.letter.segments[0].connectors)):
                p1 = self.letter.segments[0].nodes[i]
                if len(self.letter.segments[0].connectors)-1 == i:
                    p2 = p1 = self.letter.segments[0].nodes[0]
                else:
                    p2 = self.letter.segments[0].nodes[i+1]
                dist = distance_to_line_segment(p1,p2,Node(x,y))
                connector = self.letter.segments[0].connectors[i]
                debug.send(dist)
                if dist <= 3:
                    if connector.selected:
                        connector.deselect()
                        self.num_selected -= 1
                        self.mode = "selection_simple" if self.num_selected == 1 else "normal" if self.num_selected == 0 else self.mode
                        if self.mode == "normal":
                            self.selection_type = None
                        mode = None
                    else:
                        self.mode = "selection_simple" if self.mode == "normal" else "selection_multiple"
                        self.selection_type =  "connector"
                        self.num_selected += 1
                        connector.select()
                        mode = None
            if mode != None and self.selection_type == "connector":
                self.deselect_all_connectors()
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
            elif mode == "normal":
                self.letter.segments[0].nodes.append(EditorNode(x,y))
                self.letter.segments[0].connectors.append(EditorConnector())
        self.update()
    def draw(self):
        editor_draw(self.letter,self.canvas)
        self.recursive_line_dist_check()
    def move_selection(self,x,y,is_relative=True):
        if self.mode == "normal":
            return
        if is_relative:
            for node in self.letter.segments[0].nodes:
                if node.selected:
                    node.x += x
                    node.y += y
                    node.deselect()
        self.mode = "normal"
        self.update()
    def delete_selection(self):
        if self.mode == "normal":
            return
        nodes_copy = self.letter.segments[0].nodes[:]
        for node in self.letter.segments[0].nodes:
            if node.selected:
                nodes_copy.remove(node)
        self.letter.segments[0].nodes = nodes_copy
        self.mode = "normal"
        self.update()
    def deselect_all_connectors(self):
        for connector in self.letter.segments[0].connectors:
            if connector.selected: connector.deselect()
    def deselect_all_nodes(self):
        for node in self.letter.segments[0].nodes:
            if node.selected: node.deselect()
    def recursive_line_dist_check(self):
        for x in range(-35,35):
            x *= 10
            for y in range(-30,30):
                y *= 10
                for i in range(0,len(self.letter.segments[0].connectors)):
                    p1 = self.letter.segments[0].nodes[i]
                    if len(self.letter.segments[0].connectors)-1 == i:
                        p2 = p1 = self.letter.segments[0].nodes[0]
                    else:
                        p2 = self.letter.segments[0].nodes[i+1]
                    dist = distance_to_line_segment(p1,p2,Node(x,y))
                    if dist <= 3:
                        self.canvas.create_oval(x+350, y+300, x+350 + 3, y +300 + 3, fill="red")
                    else:
                        self.canvas.create_oval(x+350, y+300, x+350 + 3, y +300 + 3, fill="green")



class Node():
    def __init__(self,x,y):
        self.x = x
        self.y = y
class EditorNode(Node):
    def __init__(self,x,y,size=5,color="black"):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.start_size = size
        self.start_color = color
        self.selected = False
    def deselect(self):
        self.size = self.start_size
        self.color = self.start_color
        self.selected = False
    def select(self):
        self.size = self.start_size + 1
        self.color = "#156185"
        self.selected = True

class Segment():
    def __init__(self):
        self.name = "Segment"
        self.nodes = []
        self.connectors = []

class Connector():
    def __init__(self,type="LINE"):
        if type not in ["LINE","BEZIER"]:
            debug.send("INCORRECT CONNECTOR TYPE!")
            type = "LINE"
        self.type = type
        self.anchors = None
class EditorConnector(Connector):
    def __init__(self,type="LINE",width=3,color="#3d3d3d"):
        if type not in ["LINE","BEZIER"]:
            debug.send("INCORRECT CONNECTOR TYPE!")
            type = "LINE"
        self.type = type
        self.anchors = None
        self.width = width
        self.color = color
        self.start_width = width
        self.start_color = color
        self.selected = False
    def deselect(self):
        self.width = self.start_width
        self.color = self.start_color
        self.selected = False
    def select(self):
        self.width = self.start_width + 1
        self.color = "#707070"
        self.selected = True

class Letter():
    def __init__(self):
        self.segments = []
def draw_letter(letter,canvas,size,pos,draw_nodes=True):
        x,y = pos
        for segment in letter.segments:
            last_node = None
            for i in range(0,len(segment.nodes)):
                if len(segment.nodes) == 1:
                    break
                node = segment.nodes[i]
                if last_node != None:
                    connector = segment.connectors[i-1]
                    canvas.create_line(x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size, fill=connector.color, width=connector.width, tags="l_line")
                last_node = node
            if len(segment.nodes) > 1:
                    node = segment.nodes[0]
                    connector = segment.connectors[-1]
                    canvas.create_line(x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size, fill=connector.color, width=connector.width, tags="l_line")
            if draw_nodes:
                for node in segment.nodes:
                    canvas.create_oval(x + node.x*size - node.size, y + node.y*size - node.size, x + node.x*size + node.size, y + node.y*size + node.size, fill=node.color, tags="l_node")
def editor_draw(letter,canvas):
    draw_letter(letter,canvas,1,[350,300])

def draw_bezier(node1,node2,anchor1,anchor2,canvas):
    #Modified code from: https://stackoverflow.com/a/50302363
    x_start = node1.x
    y_start = node1.y

    n = 50
    for i in range(50):
        t = i / n
        x = (node1.x * (1-t)**3 + anchor1.x * 3 * t * (1-t)**2 + anchor2.x * 3 * t**2 * (1-t) + node2.x * t**3)
        y = (node1.y * (1-t)**3 + anchor1.y * 3 * t * (1-t)**2 + anchor2.y * 3 * t**2 * (1-t) + node2.y * t**3)

        canvas.create_line(x, y, x_start, y_start)
        x_start = x
        y_start = y

def distance_to_line_segment(line_p1,line_p2,point):
    """
    Calculate the shortest distance from a point (Node point) to a line segment
    defined by (Node line_p1) and (Node line_p1).
    """
    x1,y1 = line_p1.x,line_p1.y
    x2,y2 = line_p2.x,line_p2.y
    x3,y3 = point.x,point.y
    # Calculate the length squared of the line segment
    line_length_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2

    if line_length_squared == 0:
        # The line segment is a single point
        return sqrt((x3 - x1) ** 2 + (y3 - y1) ** 2)

    # Project point onto the line segment, computing t
    t = max(0, min(1, ((x3 - x1) * (x2 - x1) + (y3 - y1) * (y2 - y1)) / line_length_squared))
    
    # Find the projection point on the line
    projection_x = x1 + t * (x2 - x1)
    projection_y = y1 + t * (y2 - y1)

    # Calculate the distance from the point to the projection
    return sqrt((x3 - projection_x) ** 2 + (y3 - projection_y) ** 2)
