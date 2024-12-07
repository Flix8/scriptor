from math import sqrt
class EditorCanvas():
    def __init__(self,canvas):
        self.canvas = canvas
        self.canvas.bind("<Button-1>", self.on_click)
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
                self.letter.segments[0].nodes.append(Node(x,y))
        self.update()
        print(self.mode)
    def update(self):
        self.clear()
        self.letter.draw_letter_editor(self.canvas)
    def clear(self,tag="grid",del_all_except_tag=True):
        if not del_all_except_tag:
            self.canvas.delete(tag)
        else:
            for item in self.canvas.find_all():
                if tag not in self.canvas.gettags(item):
                    self.canvas.delete(item)
class Node():
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
class Letter():
    def __init__(self):
        self.segments = []
    def draw(self,canvas,size,pos,draw_nodes=True):
        x,y = pos
        for segment in self.segments:
            last_node = None
            for node in segment.nodes:
                if last_node != None:
                    canvas.create_line(x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size, fill="#3d3d3d", width=3, tags="l_line")
                last_node = node
            if draw_nodes:
                for node in segment.nodes:
                    canvas.create_oval(x + node.x*size - node.size, y + node.y*size - node.size, x + node.x*size + node.size, y + node.y*size + node.size, fill=node.color, tags="l_node")
    def draw_letter_editor(self,canvas):
        self.draw(canvas,1,[350,300])