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
        self.num_selected = 0
    def on_click(self,event):
        x,y = event.x-350, event.y-300
        selected = False
        for node in self.letter.segments[0].nodes:
            dist = sqrt((x-node.x)**2+(y-node.y)**2)
            if dist <= node.size + 3:
                if node.selected:
                    node.deselect()
                    self.num_selected -= 1
                    self.mode = "selection_simple" if self.num_selected == 1 else "normal" if self.num_selected == 0 else self.mode
                else:
                    node.select()
                    self.mode = "selection_simple" if self.mode == "normal" else "selection_multiple"
                    self.num_selected += 1
                selected = True
        if not selected:
            if self.mode != "normal":
                for node in self.letter.segments[0].nodes:
                    if node.selected:
                        node.deselect()
                self.mode = "normal"
                self.num_selected
            else:
                self.letter.segments[0].nodes.append(EditorNode(x,y))
                self.letter.segments[0].connectors.append(Connector())
        self.update()
    def draw(self):
        editor_draw(self.letter,self.canvas)
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
class Letter():
    def __init__(self):
        self.segments = []
def draw_letter(letter,canvas,size,pos,draw_nodes=True):
        x,y = pos
        for segment in letter.segments:
            last_node = None
            for i in range(0,len(segment.nodes)):
                node = segment.nodes[i]
                connector = segment.connectors[i]
                debug.send(connector.type)
                if last_node != None:
                    canvas.create_line(x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size, fill="#3d3d3d", width=3, tags="l_line")
                last_node = node
            if len(segment.nodes) > 1:
                    node = segment.nodes[0]
                    canvas.create_line(x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size, fill="#3d3d3d", width=3, tags="l_line")
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