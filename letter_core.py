from math import sqrt
import debug_console as debug
class ScriptorCanvas():
    def __init__(self,canvas):
        self.canvas = canvas
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>",self.on_click_release)
        self.canvas.bind("<Motion>",self.on_move)
        self.canvas.bind("<B1-Motion>",self.on_drag)
    def on_click(self,event):
        pass
    def on_click_release(self,event):
        pass
    def on_move(self,event):
        pass
    def on_drag(self,event):
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
    def on_key(self,history):
        pass
    def draw(self):
        pass

class EditorCanvas(ScriptorCanvas):
    def __init__(self,canvas):
        super().__init__(canvas)
        self.selected_segment = 0
        self.letter_name = "Unnamed"
        self.keys_pressed = []
        self.cursor = EditorNode(0,0,5,"green")
        self.cursor_step_size = 20
        self.step_size_options = [20,10,5,1] #Needs to be imported from settings
        self.letter = Letter()
        self.letter.segments.append(Segment())
        self.saved = True
        self.draw_nodes = True
        self.configuration_data = None
        self.light_reset()
    def load_letter(self,letter,name):
        self.letter_name = name
        self.light_reset()
        self.letter = letter
        self.update()
    def light_reset(self,do_reload_segments=True):
        self.deselect_all_connectors()
        self.deselect_all_nodes()
        #Canvas Interaction Stuff___________
        self.last_node_created = None
        self.last_pos = None
        self.to_deselect = None
        self.info_selected_anchor_point = None
        #____________________
        self.mode = "normal" #normal/selection_simple/selection_multiple
        self.selection_type = None #node/None/connector
        self.num_selected = 0
        self.configuration_data = [0]
        if do_reload_segments: self.reload_segments = True
    def on_key(self,history):
        for type,key in history:
            if type == "down" and key not in self.keys_pressed:
                self.keys_pressed.append(key)
            elif type == "up" and key in self.keys_pressed: #This might behave weirdly
                self.keys_pressed.remove(key)
        self.update_step_size()
        self.process_key_presses()
    def process_key_presses(self):
        if "entf" in self.keys_pressed:
            self.delete_selection()
            self.keys_pressed.remove("entf")
        if "backspace" in self.keys_pressed:
            self.delete_selection()
            self.keys_pressed.remove("backspace")
        if "b" in self.keys_pressed:
            if self.selection_type == "connector":
                for connector in self.letter.segments[self.selected_segment].connectors:
                    if connector.selected and connector.type == "LINE":
                        connector.set_type("BEZIER")
                self.deselect_all_connectors()
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
                self.configuration_data = [0]
                self.update()
            self.keys_pressed.remove("b")
        if "l" in self.keys_pressed:
            if self.selection_type == "connector":
                for connector in self.letter.segments[self.selected_segment].connectors:
                    if connector.selected and connector.type == "BEZIER":
                        connector.set_type("LINE")
                self.deselect_all_connectors()
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
                self.configuration_data = [0]
                self.update()
            self.keys_pressed.remove("l")
    def on_click(self,event):
        real_x,real_y = event.x-350,event.y-300
        x,y = self.calculate_snapped_position(event.x-350, event.y-300)
        self.last_pos = (x,y)
        selected = False
        for info in self.get_all_selected_anchor_points():
            x,y,index,point = info
            dist = sqrt((real_x-x)**2+(real_y-y)**2)
            if dist <= 6:
                self.info_selected_anchor_point = (index,point)
                return
        for node in self.letter.segments[self.selected_segment].nodes:
            dist = sqrt((real_x-node.x)**2+(real_y-node.y)**2)
            if dist <= node.size + 3:
                if self.selection_type == "connector":
                    self.deselect_all_connectors()
                    self.mode = "normal"
                    self.selection_type = None
                    self.num_selected = 0
                if node.selected:
                    self.to_deselect = node
                else:
                    if self.mode != "normal" and not "shift" in self.keys_pressed:
                        self.mode = "normal"
                        self.deselect_all_nodes()
                    node.select()
                    self.mode = "selection_simple" if self.mode == "normal" else "selection_multiple"
                    if self.mode == "selection_simple":
                        self.selection_type = "node"
                        #Sending to Configuration
                        self.configuration_data = [1,node.x,node.y]
                    elif self.mode == "selection_multiple":
                        #Sending to Configuration
                        sendx,sendy = 0,0
                        num = 0
                        for node in self.letter.segments[self.selected_segment].nodes:
                            if node.selected:
                                sendx += node.x
                                sendy += node.y
                                num += 1
                        self.configuration_data = [1,sendx/num,sendy/num]
                    self.num_selected += 1
                selected = True
                break                
        if not selected:
            mode = self.mode
            if mode != "normal" and self.selection_type == "node":
                self.deselect_all_nodes()
                self.last_pos = None
                self.configuration_data = [0]
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
            for i,connector in enumerate(self.letter.segments[self.selected_segment].connectors):
                p1 = self.letter.segments[self.selected_segment].nodes[i]
                p2 = self.letter.segments[self.selected_segment].nodes[(i+1)%len(self.letter.segments[self.selected_segment].connectors)]
                dist = distance_to_line_segment(p1,p2,Node(real_x,real_y))
                if dist <= 6:
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
                    if self.mode == "selection_simple":
                        for i,connector in enumerate(self.letter.segments[self.selected_segment].connectors):
                            if connector.selected:
                                p1 = self.letter.segments[self.selected_segment].nodes[i]
                                p2 = self.letter.segments[self.selected_segment].nodes[(i+1)%len(self.letter.segments[self.selected_segment].connectors)]
                                #Sending to Configuration
                                if connector.type == "LINE":
                                    self.configuration_data = [2,p1.x,p1.y,p2.x,p2.y]
                                else:
                                    self.configuration_data = [4,p1.x,p1.y,p2.x,p2.y,connector.anchors[0].x,connector.anchors[0].y,connector.anchors[1].x,connector.anchors[1].y]
                                break
                    else:
                        self.configuration_data = [0]
            if mode != None and self.selection_type == "connector":
                self.deselect_all_connectors()
                self.last_pos = None
                self.mode = "normal"
                self.configuration_data = [0]
                self.selection_type = None
                self.num_selected = 0
            elif mode == "normal":
                self.saved = False
                new_node = EditorNode(x,y)
                self.last_node_created = new_node
                self.letter.segments[self.selected_segment].nodes.append(new_node)
                self.letter.segments[self.selected_segment].connectors.append(EditorConnector())
        self.update()
    def on_click_release(self, event):
        self.last_node_created = None
        self.last_pos = None
        self.info_selected_anchor_point = None
        if isinstance(self.to_deselect,EditorNode):
            node = self.to_deselect
            node.deselect()
            self.num_selected -= 1
            self.mode = "selection_simple" if self.num_selected == 1 else "normal" if self.num_selected == 0 else self.mode
            if self.mode == "normal":
                self.configuration_data = [0]
                self.selection_type = None
            elif self.mode == "selection_simple":
                #Sending to Configuration
                for node in self.letter.segments[self.selected_segment].nodes:
                    if node.selected:
                        self.configuration_data = [1,node.x,node.y]
                        break
            elif self.mode == "selection_multiple":
                #Sending to Configuration
                sendx,sendy = 0,0
                num = 0
                for node in self.letter.segments[self.selected_segment].nodes:
                    if node.selected:
                        sendx += node.x
                        sendy += node.y
                        num += 1
                self.configuration_data = [1,sendx/num,sendy/num]
            self.to_deselect = None
            self.update()
    def on_move(self,event):
        if self.selection_type == None:
            self.cursor.x, self.cursor.y = self.calculate_snapped_position(event.x-350,event.y-300)
            self.update()
            draw_node(self.canvas,350,300,self.cursor,1,"cursor",color=self.cursor.color)
            self.cursor.x = -10
            self.cursor.y = -10
    def on_drag(self,event):
        x,y = self.calculate_snapped_position(event.x-350, event.y-300)
        if isinstance(self.last_node_created,EditorNode):
            self.last_node_created.x = x
            self.last_node_created.y = y
            self.update()
        if isinstance(self.last_pos,tuple):
            self.saved = False
            dx = x-self.last_pos[0]
            dy = y-self.last_pos[1]
            self.last_pos = (x,y)
            if isinstance(self.info_selected_anchor_point,tuple):
                index,point = self.info_selected_anchor_point
                self.letter.segments[self.selected_segment].connectors[index].anchors[point].x += dx
                self.letter.segments[self.selected_segment].connectors[index].anchors[point].y += dy
                if point == 0:
                    self.configuration_data = [4,None,None,None,None,self.letter.segments[self.selected_segment].connectors[index].anchors[0].x,self.letter.segments[self.selected_segment].connectors[index].anchors[0].y,None,None]
                else:
                    self.configuration_data = [4,None,None,None,None,None,None,self.letter.segments[self.selected_segment].connectors[index].anchors[1].x,self.letter.segments[self.selected_segment].connectors[index].anchors[1].y]
            elif self.selection_type != "connector":
                self.to_deselect = None
                for node in self.letter.segments[self.selected_segment].nodes:
                    if node.selected:
                        node.x += dx
                        node.y += dy
                sendx,sendy = 0,0
                num = 0
                for node in self.letter.segments[self.selected_segment].nodes:
                    if node.selected:
                        sendx += node.x
                        sendy += node.y
                        num += 1
                if num == 0:
                    sendx = x
                    sendy = y
                    num = 1
                self.configuration_data = [1,sendx/num,sendy/num]
            self.update()
    def draw(self):
        editor_draw(self.letter,self.canvas,self.selected_segment,self.draw_nodes)
    def delete_selection(self) -> None:
        if self.mode == "normal":
            return
        self.saved = False
        nodes_copy = self.letter.segments[self.selected_segment].nodes[:]
        connectors_copy = self.letter.segments[self.selected_segment].connectors[:]
        if self.selection_type == "node":
            for index,node in enumerate(self.letter.segments[self.selected_segment].nodes):
                if node.selected:
                    nodes_copy.remove(node)
                    connectors_copy.remove(self.letter.segments[self.selected_segment].connectors[index])
        else:
            for index,connector in enumerate(self.letter.segments[self.selected_segment].connectors):
                if connector.selected:
                    connectors_copy.remove(connector)
                    nodes_copy.remove(self.letter.segments[self.selected_segment].nodes[index])
        self.letter.segments[self.selected_segment].nodes = nodes_copy
        self.letter.segments[self.selected_segment].connectors = connectors_copy
        self.light_reset(False)
        self.update()
    def deselect_all_connectors(self):
        for connector in self.letter.segments[self.selected_segment].connectors:
            if connector.selected: connector.deselect()
    def deselect_all_nodes(self):
        for node in self.letter.segments[self.selected_segment].nodes:
            if node.selected: node.deselect()
    def calculate_snapped_position(self,x,y) -> tuple:
        x = (x//self.cursor_step_size)*self.cursor_step_size
        y = (y//self.cursor_step_size)*self.cursor_step_size
        return x,y
    def update_step_size(self):
        if "shift" in self.keys_pressed and "ctrl" in self.keys_pressed:
            self.cursor_step_size = self.step_size_options[3]
        elif "ctrl" in self.keys_pressed:
            self.cursor_step_size = self.step_size_options[2]
        elif "shift" in self.keys_pressed:
            self.cursor_step_size = self.step_size_options[1]
        else:
            self.cursor_step_size = self.step_size_options[0]
    def get_all_selected_anchor_points(self) -> list:
        #Structure: x, y, index in connectors, first or second point
        anchor_points = []
        for i in range(0,len(self.letter.segments[self.selected_segment].connectors)):
            connector = self.letter.segments[self.selected_segment].connectors[i]
            if connector.selected and connector.type == "BEZIER":
                x = connector.anchors[0].x + self.letter.segments[self.selected_segment].nodes[i].x
                y = connector.anchors[0].y + self.letter.segments[self.selected_segment].nodes[i].y
                anchor_points.append((x,y,i,0))
                x = connector.anchors[1].x + self.letter.segments[self.selected_segment].nodes[(i+1)%len(self.letter.segments[self.selected_segment].nodes)].x
                y = connector.anchors[1].y + self.letter.segments[self.selected_segment].nodes[(i+1)%len(self.letter.segments[self.selected_segment].nodes)].y
                anchor_points.append((x,y,i,1))
        return anchor_points
    def set_draw_nodes(self,value:bool):
        self.draw_nodes = value




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
        self.set_type(type)
    def set_type(self,type):
        if type not in ["LINE","BEZIER"]:
            debug.send("INCORRECT CONNECTOR TYPE!")
            type = "LINE"
        self.type = type
        self.anchors = None if type == "LINE" else [Node(0,0),Node(0,0)]

class EditorConnector(Connector):
    def __init__(self,type="LINE",width=3,color="#3d3d3d"):
        self.set_type(type)
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
        self.groups = []

class Group():
    def __init__(self,name,color="blue",parent="None"):
        self.name = name
        self.color = color
        self.parent = parent if parent != "None" else None
    def __str__(self):
        return f"{self.name}:{self.color}:{self.parent if self.parent != None else "None"}"
    
def draw_letter(letter,canvas,size,pos,draw_nodes=True,selected_segment_index=None,color_letter=None,width_letter=None,base_color="black"):
        x,y = pos
        for segment_index, segment in enumerate(letter.segments):
            last_node = None
            sel = (segment_index == selected_segment_index) if selected_segment_index != None else True #Is not selected?
            for i,node in enumerate(segment.nodes):
                if len(segment.nodes) == 1:
                    break
                if last_node != None:
                    connector = segment.connectors[i-1]
                    if isinstance(connector,EditorConnector):
                        color = connector.color if sel else base_color
                        width = connector.width
                    else:
                        color = color_letter if color_letter != None else base_color
                        width = width_letter
                    if connector.type == "LINE":
                        canvas.create_line(x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size, fill=color, width=width, tags="l_line")
                    else:
                        if isinstance(connector,EditorConnector) and connector.selected:
                            anchor1 = Node(connector.anchors[0].x*size,connector.anchors[0].y*size)
                            anchor2 = Node(connector.anchors[1].x*size,connector.anchors[1].y*size)
                            canvas.create_oval(x + node.x + 5*size + anchor2.x, y + node.y + 5*size + anchor2.y, x + node.x - 5*size + anchor2.x, y + node.y - 5*size + anchor2.y, fill="red", tags="l_node")
                            canvas.create_oval(x + last_node.x + 5*size + anchor1.x, y + last_node.y + 5*size + anchor1.y, x + last_node.x - 5*size + anchor1.x, y + last_node.y - 5*size + anchor1.y, fill="red", tags="l_node")
                        draw_bezier(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],canvas,width,color)
                last_node = node
            if len(segment.nodes) > 1:
                    node = segment.nodes[0]
                    connector = segment.connectors[-1]
                    if isinstance(connector,EditorConnector):
                        color = connector.color if sel else base_color
                        width = connector.width
                    else:
                        color = color_letter if color_letter != None else base_color
                        width = width_letter
                    if connector.type == "LINE":
                        canvas.create_line(x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size, fill=color, width=width, tags="l_line")
                    else:
                        if isinstance(connector,EditorConnector) and connector.selected:
                            anchor1 = Node(connector.anchors[0].x*size,connector.anchors[0].y*size)
                            anchor2 = Node(connector.anchors[1].x*size,connector.anchors[1].y*size)
                            canvas.create_oval(x + node.x + 5*size + anchor2.x, y + node.y + 5*size + anchor2.y, x + node.x - 5*size + anchor2.x, y + node.y - 5*size + anchor2.y, fill="red", tags="l_node")
                            canvas.create_oval(x + last_node.x + 5*size + anchor1.x, y + last_node.y + 5*size + anchor1.y, x + last_node.x - 5*size + anchor1.x, y + last_node.y - 5*size + anchor1.y, fill="red", tags="l_node")
                        draw_bezier(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],canvas,width,color)
            if draw_nodes:
                for node in segment.nodes:
                    if isinstance(node,EditorNode):
                        color = node.color if sel else base_color
                    else:
                        color = color_letter if color_letter != None else base_color
                    draw_node(canvas,x,y,node,size,sel=sel,color=color)
def editor_draw(letter,canvas,selected_segment_index,draw_nodes=True):
    draw_letter(letter,canvas,1,[350,300],draw_nodes,selected_segment_index if draw_nodes else None,base_color="gray" if draw_nodes else "black")

def draw_node(canvas,x,y,node,size,tag="l_node",sel=True,color="gray"):
    canvas.create_oval(x + node.x*size - node.size, y + node.y*size - node.size, x + node.x*size + node.size, y + node.y*size + node.size, fill=color if sel else "gray", tags=tag)
def draw_bezier(posx,posy,abs_node1,abs_node2,size,rel_anchor1,rel_anchor2,canvas,width=3,color="black"):
    #Modified code from: https://stackoverflow.com/a/50302363
    node1 = Node(posx + abs_node1.x * size,posy + abs_node1.y * size)
    node2 = Node(posx + abs_node2.x * size,posy + abs_node2.y * size)
    x_start = node1.x
    y_start = node1.y
    anchor1 = Node(rel_anchor1.x * size + node1.x,rel_anchor1.y * size + node1.y)
    anchor2 = Node(rel_anchor2.x * size + node2.x,rel_anchor2.y * size + node2.y)
    n = 50
    for i in range(n):
        t = i / n
        x = (node1.x * (1-t)**3 + anchor1.x * 3 * t * (1-t)**2 + anchor2.x * 3 * t**2 * (1-t) + node2.x * t**3)
        y = (node1.y * (1-t)**3 + anchor1.y * 3 * t * (1-t)**2 + anchor2.y * 3 * t**2 * (1-t) + node2.y * t**3)

        canvas.create_line(x, y, x_start, y_start,fill=color, width=width,tags="l_line")
        x_start = x
        y_start = y

def distance_to_line_segment(line_p1,line_p2,point) -> float:
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
