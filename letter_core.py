from math import sqrt, sin, cos, radians
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
        self.closest_node_index = None
        self.keys_pressed = []
        self.cursor = EditorNode(0,0,5,"green")
        self.cursor_step_size = 20
        self.step_size_options = [20,10,5,1] #Needs to be imported from settings
        self.letter = Letter()
        self.letter.segments.append(Segment())
        self.saved = True
        self.active = True
        self.draw_nodes = True
        self.configuration_data = None
        self.center_edits = Node(0,0)
        self.light_reset()
    def load_letter(self,letter,name):
        self.letter_name = name
        self.light_reset()
        self.letter = letter
        self.selected_segment = 0
        self.update()
    def light_reset(self,do_reload_segments=True):
        self.deselect_all_connectors()
        self.deselect_all_nodes()
        #Canvas Interaction Stuff___________
        self.last_node_created = None
        self.last_pos = None
        self.to_deselect = None
        self.info_selected_anchor_point = None
        self.closest_node_index = None
        #____________________
        self.mode = "normal" #normal/selection_simple/selection_multiple
        self.selection_type = None #node/None/connector
        self.num_selected = 0
        self.configuration_data = [0]
        self.center_edits = Node(0,0)
        if do_reload_segments: self.reload_segments = True
    def on_key(self,history):
        for type,key in history:
            if type == "down" and key not in self.keys_pressed:
                self.keys_pressed.append(key)
            elif type == "up" and key in self.keys_pressed: #This might behave weirdly
                self.keys_pressed.remove(key)
        self.update_step_size()
        self.process_key_presses()
    def process_key_presses(self,disregard_focus=False):
        #str(self.canvas.focus_get()).startswith(".!toplevel") or 
        if not disregard_focus and (self.canvas.focus_get() == None or str(self.canvas.focus_get()) != ".!frame4.!canvas") or not self.active:
            return
        if "entf" in self.keys_pressed:
            self.delete_selection()
            self.keys_pressed.remove("entf")
        if "backspace" in self.keys_pressed:
            self.delete_selection()
            self.keys_pressed.remove("backspace")
        if "b" in self.keys_pressed:
            if self.selection_type == "connector":
                for connector in self.letter.segments[self.selected_segment].connectors:
                    if connector.selected and connector.type != "BEZIER":
                        connector.set_type("BEZIER")
                self.deselect_all_connectors()
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
                self.configuration_data = [0]
                self.update()
            self.keys_pressed.remove("b")
        if "c" in self.keys_pressed:
            if self.selection_type == "connector":
                for connector in self.letter.segments[self.selected_segment].connectors:
                    if connector.selected and connector.type != "CIRCLE":
                        connector.set_type("CIRCLE")
                self.deselect_all_connectors()
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
                self.configuration_data = [0]
                self.update()
            self.keys_pressed.remove("c")
        if "l" in self.keys_pressed:
            if self.selection_type == "connector":
                for connector in self.letter.segments[self.selected_segment].connectors:
                    if connector.selected and connector.type != "LINE":
                        connector.set_type("LINE")
                self.deselect_all_connectors()
                self.mode = "normal"
                self.selection_type = None
                self.num_selected = 0
                self.configuration_data = [0]
                self.update()
            self.keys_pressed.remove("l")
    def on_click(self,event):
        if not self.active: return

        self.canvas.focus_set()
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
                if connector.type == "LINE":
                    dist = distance_to_line_segment(p1,p2,Node(real_x,real_y))
                elif connector.type == "BEZIER":
                    dist = distance_to_bezier(p1,p2,connector.anchors[0],connector.anchors[1],Node(real_x,real_y))
                else:
                    dist = distance_to_half_circle(p1,p2,connector.direction,Node(real_x,real_y))
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
                                elif connector.type == "BEZIER":
                                    self.configuration_data = [4,p1.x,p1.y,p2.x,p2.y,connector.anchors[0].x,connector.anchors[0].y,connector.anchors[1].x,connector.anchors[1].y]
                                else:
                                    #5 -> Doing special thing (Hiding y coordinate for third)
                                    self.configuration_data = [5,p1.x,p1.y,p2.x,p2.y,connector.direction,None]
                                break
                    else:
                        self.configuration_data = [0]
                    break
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
                if self.closest_node_index is not None:
                    debug.send("inserting on index",self.closest_node_index)
                    self.letter.segments[self.selected_segment].nodes.insert(self.closest_node_index,new_node)
                    self.letter.segments[self.selected_segment].connectors.insert(self.closest_node_index,EditorConnector())
                else:
                    self.letter.segments[self.selected_segment].nodes.append(new_node)
                    self.letter.segments[self.selected_segment].connectors.append(EditorConnector())
        self.update()
    def on_click_release(self, event):
        if not self.active: return
        
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
        if not self.active: return
        
        if self.selection_type == None:
            self.cursor.x, self.cursor.y = self.calculate_snapped_position(event.x-350,event.y-300)
            if len(self.letter.segments[self.selected_segment].nodes) != 0:
                min_length = 0
                node_index = -1
                for i,connector in enumerate(self.letter.segments[self.selected_segment].connectors):
                    p1 = self.letter.segments[self.selected_segment].nodes[i]
                    p2 = self.letter.segments[self.selected_segment].nodes[(i+1)%len(self.letter.segments[self.selected_segment].connectors)]
                    if connector.type == "LINE":
                        dist = distance_to_line_segment(p1,p2,self.cursor)
                    elif connector.type == "BEZIER":
                        dist = distance_to_bezier(p1,p2,connector.anchors[0],connector.anchors[1],self.cursor)
                    else:
                        dist = distance_to_half_circle(p1,p2,connector.direction,self.cursor)
                    if node_index == -1:
                        min_length = dist
                        node_index = i
                    elif dist <= min_length:
                        min_length = dist
                        node_index = i
                if node_index != len(self.letter.segments[self.selected_segment].nodes) - 1:
                    self.closest_node_index = node_index + 1
                else:
                    self.closest_node_index = 0
            else:
                self.closest_node_index = None             
            self.update()
            if self.closest_node_index is not None:
                node1 = self.letter.segments[self.selected_segment].nodes[self.closest_node_index-1]
                node2 = self.letter.segments[self.selected_segment].nodes[self.closest_node_index]
                existing_connector = self.letter.segments[self.selected_segment].connectors[self.closest_node_index-1]
                new_connector_with_first_node = length(node1-self.cursor) >= length(node2-self.cursor)
                if new_connector_with_first_node:
                    node1,node2 = node2,node1
                if existing_connector.type == "LINE":
                    draw_line(self.canvas,350,300,node1,self.cursor,1,"#4a9094")
                elif existing_connector.type == "BEZIER":
                    draw_bezier(350,300,node1,self.cursor,1,existing_connector.anchors[0],existing_connector.anchors[1],self.canvas,color="#4a9094")
                else:
                    draw_half_circle(350,300,node1,self.cursor,1,existing_connector.direction if not new_connector_with_first_node else -existing_connector.direction,self.canvas,color="#4a9094")
                draw_line(self.canvas,350,300,node2,self.cursor,1,"#4a9094")
            draw_node(self.canvas,350,300,self.cursor,1,"cursor",color=self.cursor.color)
            self.cursor.x = -10
            self.cursor.y = -10
    def on_drag(self,event):
        if not self.active: return
        
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
        editor_draw(self.letter,self.canvas,self.selected_segment,self.draw_nodes,self.center_edits)
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
    def rotate_selection(self,angle,center=(0,0),use_center_edits=True) -> None:
        if use_center_edits:
            center = (self.center_edits.x,self.center_edits.y)
        if self.selection_type == "node":
            for node in self.letter.segments[self.selected_segment].nodes:
                if node.selected:
                    node.x -= center[0]
                    node.y -= center[1]
                    rotated_x = node.x * cos(radians(angle)) - node.y * sin(radians(angle))
                    rotated_y = node.y * cos(radians(angle)) + node.x * sin(radians(angle))
                    node.x = rotated_x
                    node.y = rotated_y
                    node.x += center[0]
                    node.y += center[1]
        self.light_reset(False)
        self.update()
    def mirror_selection(self,x_axis=False,y_axis=True,center=(0,0),use_center_edits=True) -> None:
        if use_center_edits:
            center = (self.center_edits.x,self.center_edits.y)
        if self.selection_type == "node":
            for node in self.letter.segments[self.selected_segment].nodes:
                if node.selected:
                    node.x -= center[0]
                    node.y -= center[1]
                    if x_axis:
                        node.y = -node.y
                    if y_axis:
                        node.x = -node.x
                    node.x += center[0]
                    node.y += center[1]
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

class PositioningCanvas(ScriptorCanvas):
    def __init__(self,canvas):
        super().__init__(canvas)
        self.letter_name = "Unnamed"
        self.keys_pressed = []
        self.cursor = EditorNode(0,0,5,"green")
        self.cursor_step_size = 20
        self.step_size_options = [20,10,5,1] #Needs to be imported from settings
        self.slots = [] #List of LetterSpaces
        self.letter = None
        self.saved = True
        self.active = False
        self.zoom = 1.0
        self.configuration_data = None
        self.light_reset()
    def load_letter(self,letter,name,reset_slots:bool=True):
        self.letter_name = name
        self.light_reset()
        self.letter = letter
        if reset_slots:
            self.slots = []
        self.update()
    def load_slots(self,slots:list=[]):
        self.slots = slots
        self.update()
    def light_reset(self,do_reload_slots=True):
        self.deselect_all_slots()
        #Canvas Interaction Stuff___________
        self.last_slot_created = None
        self.last_pos = None
        self.to_deselect = None
        #____________________
        self.mode = "normal" #normal/selection_simple/selection_multiple
        self.num_selected = 0
        self.configuration_data = [0]
        self.center_edits = Node(0,0)
        if do_reload_slots: self.reload_slots = True
    def on_key(self,history):
        for type,key in history:
            if type == "down" and key not in self.keys_pressed:
                self.keys_pressed.append(key)
            elif type == "up" and key in self.keys_pressed: #This might behave weirdly
                self.keys_pressed.remove(key)
        self.update_step_size()
        self.process_key_presses()
    def process_key_presses(self,disregard_focus=False):
        #str(self.canvas.focus_get()).startswith(".!toplevel") or 
        if not disregard_focus and (self.canvas.focus_get() == None or str(self.canvas.focus_get()) != ".!frame4.!canvas") or not self.active:
            return
        if "entf" in self.keys_pressed:
            self.delete_selection()
            self.keys_pressed.remove("entf")
        if "backspace" in self.keys_pressed:
            self.delete_selection()
            self.keys_pressed.remove("backspace")
    def on_click(self,event):
        if not self.active: return
        
        self.canvas.focus_set()
        real_x,real_y = event.x-350,event.y-300
        real_x *= self.zoom
        real_y *= self.zoom
        x,y = self.calculate_snapped_position(event.x-350, event.y-300)
        x *= self.zoom
        y *= self.zoom
        self.last_pos = (x,y)
        selected = False
        for slot in self.slots:
            if is_inside_slot(real_x,real_y,slot):
                if slot.selected:
                    self.to_deselect = slot
                else:
                    if self.mode != "normal" and not "shift" in self.keys_pressed:
                        self.mode = "normal"
                        self.deselect_all_slots()
                    slot.selected = True
                    self.mode = "selection_simple" if self.mode == "normal" else "selection_multiple"
                    if self.mode == "selection_simple":
                        #Sending to Configuration
                        self.configuration_data = [2,slot.x,slot.y,slot.width,slot.height]
                    elif self.mode == "selection_multiple":
                        #Sending to Configuration
                        sendx,sendy = 0,0
                        num = 0
                        for slot in self.slots:
                            if slot.selected:
                                sendx += slot.x
                                sendy += slot.y
                                num += 1
                        self.configuration_data = [1,sendx/num,sendy/num]
                    self.num_selected += 1
                selected = True
                break                
        if not selected:
            mode = self.mode
            if mode != "normal":
                self.deselect_all_slots()
                self.last_pos = None
                self.configuration_data = [0]
                self.mode = "normal"
                self.num_selected = 0
            elif mode == "normal":
                self.saved = False
                new_slot = EditorLetterSpace(x,y)
                self.last_slot_created = new_slot
                self.slots.append(new_slot)
        self.update()
    def on_click_release(self, event):
        if not self.active: return
        
        self.last_slot_created = None
        self.last_pos = None
        if isinstance(self.to_deselect,EditorLetterSpace):
            slot = self.to_deselect
            slot.selected = False
            self.num_selected -= 1
            self.mode = "selection_simple" if self.num_selected == 1 else "normal" if self.num_selected == 0 else self.mode
            if self.mode == "normal":
                self.configuration_data = [0]
            elif self.mode == "selection_simple":
                #Sending to Configuration
                for slot in self.slots:
                    if slot.selected:
                        self.configuration_data = [1,slot.x,slot.y]
                        break
            elif self.mode == "selection_multiple":
                #Sending to Configuration
                sendx,sendy = 0,0
                num = 0
                for slot in self.slots:
                    if slot.selected:
                        sendx += slot.x
                        sendy += slot.y
                        num += 1
                self.configuration_data = [1,sendx/num,sendy/num]
            self.to_deselect = None
            self.update()
    def on_move(self,event):
        if not self.active: return
        
        if self.mode == "normal":
            self.cursor.x, self.cursor.y = self.calculate_snapped_position(event.x-350,event.y-300)
            self.update()
            draw_node(self.canvas,350,300,self.cursor,1,"cursor",color=self.cursor.color)
            self.cursor.x = -10
            self.cursor.y = -10
    def on_drag(self,event):
        if not self.active: return
        
        x,y = self.calculate_snapped_position(event.x-350, event.y-300)
        x *= self.zoom
        y *= self.zoom
        if isinstance(self.last_slot_created,EditorLetterSpace):
            self.last_slot_created.x = x
            self.last_slot_created.y = y
            self.update()
        if isinstance(self.last_pos,tuple):
            self.saved = False
            dx = x-self.last_pos[0]
            dy = y-self.last_pos[1]
            self.last_pos = (x,y)
            self.to_deselect = None
            for slot in self.slots:
                if slot.selected:
                    slot.x += dx
                    slot.y += dy
            sendx,sendy = 0,0
            num = 0
            for slot in self.slots:
                if slot.selected:
                    sendx += slot.x
                    sendy += slot.y
                    num += 1
            if num == 0:
                sendx = x
                sendy = y
                num = 1
            if self.mode == "selection_simple":
                self.configuration_data = [2,sendx/num,sendy/num,None,None]
            else:
                self.configuration_data = [1,sendx/num,sendy/num]
            self.update()
    def draw(self):
        positioning_draw(self.letter,self.canvas,self.slots,self.zoom)
    def delete_selection(self) -> None:
        if self.mode == "normal":
            return
        self.saved = False
        slots_copy = self.slots[:]
        for index,slot in enumerate(self.slots):
            if slot.selected:
                slots_copy.remove(slot)
        self.slots = slots_copy
        self.light_reset(False)
        self.update()
    def deselect_all_slots(self):
        for slot in self.slots:
            if slot.selected:
                slot.selected = False
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
    def zoom_changed(self):
        self.clear("base")
        self.canvas.create_line(350-200/self.zoom,300-200/self.zoom,350+200/self.zoom,300-200/self.zoom,fill="gray",tags="grid")
        self.canvas.create_line(350-200/self.zoom,300+200/self.zoom,350+200/self.zoom,300+200/self.zoom,fill="gray",tags="grid")
        self.canvas.create_line(350-200/self.zoom,300-200/self.zoom,350-200/self.zoom,300+200/self.zoom,fill="gray",tags="grid")
        self.canvas.create_line(350+200/self.zoom,300-200/self.zoom,350+200/self.zoom,300+200/self.zoom,fill="gray",tags="grid")
        self.draw()




class Node():
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __add__(self, value):
        if isinstance(value, Node):
            return Node(self.x + value.x, self.y + value.y)
        else:
            return Node(self.x + value, self.y + value)

    def __sub__(self, value):
        if isinstance(value, Node):
            return Node(self.x - value.x, self.y - value.y)
        else:
            return Node(self.x - value, self.y - value)

    def __mul__(self, value):
        if isinstance(value, Node):
            return Node(self.x * value.x, self.y * value.y)
        else:
            return Node(self.x * value, self.y * value)

    def __floordiv__(self, value):
        if isinstance(value, Node):
            return Node(self.x // value.x, self.y // value.y)
        else:
            return Node(self.x // value, self.y // value)

    def __truediv__(self, value):
        if isinstance(value, Node):
            return Node(self.x / value.x, self.y / value.y)
        else:
            return Node(self.x / value, self.y / value)

    def __repr__(self):
        return f"Node({self.x}, {self.y})"
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
        if type not in ["LINE","BEZIER","CIRCLE"]:
            debug.send("INCORRECT CONNECTOR TYPE!")
            type = "LINE"
        self.type = type
        self.anchors = None if type != "BEZIER" else [Node(0,0),Node(0,0)]
        self.direction = None if type != "CIRCLE" else 1 #1 -> Rotation clock-wise, -1 -> Rotation counter-clock-wise

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
        return f"{self.name}:{self.color}:{self.parent if self.parent != None else 'None'}"

        

class LetterSpace():
    def __init__(self,x:float=0,y:float=0,width:int=100,height:int=100,letter:str|None=None,children:list = []):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.letter = letter
        self.children = children
        self.outline_color_mode = "GLOBAL" #GLOBAL, PARENT, CUSTOM
        self.global_outline_color = ""
        self.parent_outline_color = ""
        self.custom_outline_color = ""
    def update_outline_color(self,mode="GLOBAL",color="black",is_parent_outline_color:bool=False):
        #Recursivly update all the children
        if mode == "GLOBAL" and self.global_outline_color != color:
            self.global_outline_color = color
            if is_parent_outline_color:
                self.parent_outline_color = color
            for child in self.children:
                child.update_outline_color(mode,color,self.outline_color_mode=="GLOBAL")
                if is_parent_outline_color:
                    child.update_outline_color("PARENT",color)
        if mode == "PARENT":
            self.parent_outline_color = color
            if self.outline_color_mode == "PARENT":
                for child in self.children:
                    child.update_outline_color("PARENT",color)
        if mode == "CUSTOM":
            self.custom_outline_color = color
            if is_parent_outline_color:
                self.parent_outline_color = color
            for child in self.children:
                if self.outline_color_mode == "CUSTOM":
                    child.update_outline_color("PARENT",color)
    def load_slots(self,slots:list=[]):
        self.children += slots
    def delete_slot(self,index):
        self.children.pop(index)
        
class WritingRoot():
    def __init__(self,canvas,width:int=600,height:int=600,children:list=[]):
        self.width = width
        self.height = height
        self.canvas = canvas
        self.children = children
        self.linear_children = self.make_children_linear(children) #Linear version that can be accessed with an index
    
    def get_child_with_index(self,index:int):
        return self.linear_children[index]
    
    def delete_child_with_index(self,parent_index:int,child_index:int):
        self.linear_children[parent_index].children.pop(child_index-parent_index)
        self.linear_children.pop(child_index)
    
    def load_letter_into_slot_with_index(self,letter:Letter|None,index:int):
        self.linear_children[index].letter = letter
    
    def load_slots_for_child_with_index(self,index:int,slots:list):
        cur_index = index
        for slot in slots:
            self.linear_children.insert(cur_index,slot)
            cur_index += 1
        self.linear_children[index].load_slots(slots)

    def make_children_linear(self,children:list) -> list:
        linear_children = []
        for child in children:
            self.make_slot_linear(child,linear_children)
        return linear_children
    
    def make_slot_linear(self,slot:LetterSpace,linear_children):
        linear_children.append(slot)
        for child in slot.children:
            self.make_slot_linear(child,linear_children)
    

class EditorLetterSpace():
    def __init__(self,x:float=0,y:float=0,width:int=100,height:int=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.selected = False

#Draw functions    
def draw_letter(letter:Letter,canvas,size:float,center:Node,draw_nodes=True,selected_segment_index:int|None=None,color_letter:str|None=None,width_letter=None,base_color:str|None="black"):
        x,y = center.x,center.y
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
                    elif connector.type == "BEZIER":
                        if isinstance(connector,EditorConnector) and connector.selected:
                            anchor1 = Node(connector.anchors[0].x*size,connector.anchors[0].y*size)
                            anchor2 = Node(connector.anchors[1].x*size,connector.anchors[1].y*size)
                            canvas.create_oval(x + node.x + 5*size + anchor2.x, y + node.y + 5*size + anchor2.y, x + node.x - 5*size + anchor2.x, y + node.y - 5*size + anchor2.y, fill="red", tags="l_node")
                            canvas.create_oval(x + last_node.x + 5*size + anchor1.x, y + last_node.y + 5*size + anchor1.y, x + last_node.x - 5*size + anchor1.x, y + last_node.y - 5*size + anchor1.y, fill="red", tags="l_node")
                        draw_bezier(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],canvas,width,color)
                    else:
                        draw_half_circle(x,y,last_node,node,size,connector.direction,canvas,width,color)
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
                    elif connector.type == "BEZIER":
                        if isinstance(connector,EditorConnector) and connector.selected:
                            anchor1 = Node(connector.anchors[0].x*size,connector.anchors[0].y*size)
                            anchor2 = Node(connector.anchors[1].x*size,connector.anchors[1].y*size)
                            canvas.create_oval(x + node.x + 5*size + anchor2.x, y + node.y + 5*size + anchor2.y, x + node.x - 5*size + anchor2.x, y + node.y - 5*size + anchor2.y, fill="red", tags="l_node")
                            canvas.create_oval(x + last_node.x + 5*size + anchor1.x, y + last_node.y + 5*size + anchor1.y, x + last_node.x - 5*size + anchor1.x, y + last_node.y - 5*size + anchor1.y, fill="red", tags="l_node")
                        draw_bezier(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],canvas,width,color)
                    else:
                        draw_half_circle(x,y,last_node,node,size,connector.direction,canvas,width,color)
            if draw_nodes:
                for node in segment.nodes:
                    if isinstance(node,EditorNode):
                        color = node.color if sel else base_color
                    else:
                        color = color_letter if color_letter != None else base_color
                    draw_node(canvas,x,y,node,size,sel=sel,color=color)

def editor_draw(letter,canvas,selected_segment_index,draw_nodes=True,center_edits=Node(0,0)):
    draw_letter(letter,canvas,1,Node(350,300),draw_nodes,selected_segment_index if draw_nodes else None,base_color="gray" if draw_nodes else "black")
    draw_node(canvas,350,300,EditorNode(center_edits.x,center_edits.y),1,color="purple")

def positioning_draw(letter,canvas,slots,zoom:float=1.0,center:Node=Node(0,0)):
    if letter is not None:
        draw_letter(resized_letter(letter,zoom),canvas,1,Node(350+center.x,300+center.y),False,None,base_color="black")
        
    for slot in slots:
        draw_slot(canvas,350+center.x,300+center.y,resized_letterspace(slot,zoom),1,slot.selected)

def writing_draw(writing_root:WritingRoot,canvas,zoom:float=1.0):
    canvas.create_window(0,0,window=writing_root.canvas)
    for child in writing_root.children:
        recursive_slots_draw(writing_root.canvas,child,zoom)

def recursive_slots_draw(canvas,slot:LetterSpace,zoom:float=1.0,center:Node=Node(0,0)):
    #Draw self
    if slot.letter is not None:
        draw_letter(resized_letter(slot.letter,zoom),canvas,1,Node(350+center.x,300+center.y),False,None,base_color="black")
    else:
        draw_slot(canvas,350+center.x,300+center.y,resized_letterspace(slot,zoom),1,False)
    #Draw children
    for child in slot.children:
        recursive_slots_draw(canvas,child,zoom,Node(slot.x,slot.y))

def draw_node(canvas,x,y,node,size,tag="l_node",sel=True,color="gray"):
    canvas.create_oval(x + node.x*size - node.size, y + node.y*size - node.size, x + node.x*size + node.size, y + node.y*size + node.size, fill=color if sel else "gray", tags=tag)

def draw_line(canvas,x,y,node1,node2,size,color="gray",width=3):
    canvas.create_line(x + node1.x*size, y + node1.y*size, x + node2.x*size, y + node2.y*size, fill=color, width=width, tags="l_line")

def draw_slot(canvas,x,y,slot,size,sel=True):
    canvas.create_rectangle(x+slot.x-slot.width/2*size,y+slot.y-slot.height/2*size,x+slot.x+slot.width/2*size,y+slot.y+slot.height/2*size,fill="#f7b0a8" if sel else "#bbf9fc",outline="#fc6d5d" if sel else "#8cbffa")

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

def draw_half_circle(posx,posy,abs_node1,abs_node2,size,direction,canvas,width=3,color="black"):
    node1 = Node(abs_node1.x * size,abs_node1.y * size)
    node2 = Node(abs_node2.x * size,abs_node2.y * size)
    offset = node1 + (node2-node1)/2
    x_start = node1.x - offset.x
    y_start = node1.y - offset.y
    n = 50
    for i in range(n):
        x = x_start * cos(radians(180/n*direction)) - y_start * sin(radians(180/n*direction))
        y = y_start * cos(radians(180/n*direction)) + x_start * sin(radians(180/n*direction))
        canvas.create_line(x + offset.x + posx, y + offset.y + posy, x_start + offset.x + posx, y_start + offset.y + posy,fill=color, width=width,tags="l_line")
        x_start = x
        y_start = y

#Distance calculations
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

dot = lambda v1,v2: v1.x * v2.x + v1.y * v2.y
length = lambda v: sqrt(v.x**2+v.y**2)

def distance_to_half_circle(circle_point1,circle_point2,direction,point) -> float:
    midpoint = circle_point1 + (circle_point2-circle_point1)/2
    v = circle_point1 - midpoint
    normal = Node(-v.y,v.x) * direction
    mp = point - midpoint
    if dot(mp,normal) == abs(dot(mp,normal)):
        return abs(length(mp)-length(v))
    else:
        return min(length(point-circle_point1),length(point-circle_point2))

def distance_to_bezier(node1,node2, rel_anchor1, rel_anchor2, point, n=50):
    """
    Calculate the minimum distance from a point to a cubic Bezier curve.
    The curve is defined as in draw_bezier.
    """
    anchor1 = Node(rel_anchor1.x + node1.x, rel_anchor1.y + node1.y)
    anchor2 = Node(rel_anchor2.x + node2.x, rel_anchor2.y + node2.y)

    min_dist = float('inf')
    for i in range(n + 1):
        t = i / n
        x = (node1.x * (1-t)**3 + anchor1.x * 3 * t * (1-t)**2 + anchor2.x * 3 * t**2 * (1-t) + node2.x * t**3)
        y = (node1.y * (1-t)**3 + anchor1.y * 3 * t * (1-t)**2 + anchor2.y * 3 * t**2 * (1-t) + node2.y * t**3)
        dist = sqrt((point.x - x) ** 2 + (point.y - y) ** 2)
        if dist < min_dist:
            min_dist = dist
    return min_dist

def is_inside_slot(x,y,slot:LetterSpace|EditorLetterSpace):
    return (slot.x - slot.width/2) <= x <= (slot.x + slot.width/2) and (slot.y - slot.height/2) <= y <= (slot.y + slot.height/2)

def resized_letter(letter:Letter,zoom:float) -> Letter:
    resized = Letter()
    for segment in letter.segments:
        resized_segment = Segment()
        for node in segment.nodes:
            resized_node = EditorNode(x=node.x/zoom,y=node.y/zoom,size=node.size,color=node.color)
            if node.selected:
                resized_node.select()
            else:
                resized_node.deselect()
            resized_segment.nodes.append(resized_node)
        resized_segment.name = segment.name
        resized_segment.connectors = segment.connectors
        resized.segments.append(resized_segment)
    resized.groups = letter.groups[:]
    return resized

def resized_letterspace(slot:LetterSpace|EditorLetterSpace,zoom:float):
    if type(slot) == LetterSpace:
        resized = LetterSpace()
    else:
        resized = EditorLetterSpace()
    resized.x = slot.x/zoom
    resized.y = slot.y/zoom
    resized.height = slot.height/zoom
    resized.width = slot.width/zoom
    resized.selected = slot.selected
    #Children not done yet!
    return resized