import os, json
import letter_core as l
import exporter

#WHAT THIS DOES: Handles every interaction with files. Loading, Saving, Creating things

new_language = None
all_groups = []
#______________Helper Functions__________________

def does_positioning_for_letter_exist(language:str, letter_name:str) -> bool:
    file_path = f"languages/{language}/positioning/letters/{letter_name}.json"
    return os.path.exists(file_path)

def get_group_of_letter(language:str, name_letter: str) -> list:
    file_path = f"languages/{language}/letters/{name_letter}.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    with open(file_path, 'r') as file:
        data = json.load(file)
    groups = data["groups"]
    for group_obj in all_groups:
        if group_obj.name in groups and group_obj.parent != None:
            groups.append(group_obj.parent)
    return groups

def get_group_obj(name) -> l.Group:
    for group in all_groups:
        if group.name == name:
            return group

#______Custom Classes that only store the required information for saving__________

class VeryReducedLetterSpace():
    def __init__(self,x:float=0,y:float=0,width:int=100,height:int=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class ReducedLetterSpace():
    def __init__(self,slot:l.LetterSpace,language):
        self.id = slot.id
        self.parent_id = slot.parent_id
        self.children_ids = slot.children_ids #This is not a copy, but it doesn't matter

        self.x = slot.x
        self.y = slot.y 
        self.global_x = slot.global_x
        self.global_y = slot.global_y
        self.width = slot.width
        self.height = slot.height
        self.has_a_letter = slot.letter is not None
        self.letter_name = slot.letter_name
        self.language = language
        self.letter_size = slot.letter_size

        self.outline_color_mode = slot.outline_color_mode
        self.fill_color_mode = slot.fill_color_mode
        self.custom_outline_color = slot.custom_outline_color
        self.custom_fill_color = slot.custom_fill_color
        self.letter_width = slot.letter_width

class ReducedWritingRoot():
    def __init__(self,width:int,height:int,letter_spaces:dict,root_ids:list,global_outline_color:str,global_fill_color:str, background_color:str,language_name:str):
        self.width = width
        self.height = height
        self.letter_spaces = {}
        for key, letter_space in letter_spaces.items():
            self.letter_spaces[key] = ReducedLetterSpace(letter_space,language_name)

        self.root_ids = root_ids
        self.global_outline_color = global_outline_color
        self.global_fill_color = global_fill_color
        self.background_color = background_color

class SessionData():
    def __init__(self,language,letter_editor=None,letter_config=None,text_name=None,open_frame="EDITOR"):
        self.language = language if language != "" else None
        self.letter_editor = letter_editor if letter_editor != "Unnamed" else None
        self.letter_config = letter_config if letter_config != "Unnamed" else None
        self.text_name = text_name if text_name != "Unnamed" else None
        self.open_frame = open_frame

#___________Conversion Functions_____________
def to_plain_letter(letter: l.Letter) -> l.Letter:
    #Partly written by Copilot
    plain_letter = l.Letter()
    plain_letter.groups = letter.groups
    for segment in letter.segments:
        plain_segment = l.Segment()
        plain_segment.name = segment.name
        plain_segment.is_empty = segment.is_empty
        for node in segment.nodes:
            plain_node = l.Node(node.x, node.y)
            plain_segment.nodes.append(plain_node)
        for connector in segment.connectors:
            plain_connector = l.Connector(connector.type)
            if connector.type == "BEZIER":
                plain_connector.anchors = [l.Node(connector.anchors[0].x, connector.anchors[0].y),
                                           l.Node(connector.anchors[1].x, connector.anchors[1].y)]
            elif connector.type == "CIRCLE":
                plain_connector.direction = connector.direction
            plain_segment.connectors.append(plain_connector)
        plain_letter.segments.append(plain_segment)
    return plain_letter

def to_reduced_letter_space(letter_space: l.LetterSpace|l.EditorLetterSpace) -> VeryReducedLetterSpace:
    return VeryReducedLetterSpace(letter_space.x,letter_space.y,letter_space.width,letter_space.height)

def to_reduced_writing_root(root: l.WritingRoot,language_name:str)-> ReducedWritingRoot:
    return ReducedWritingRoot(root.width,root.height,root.letter_spaces,root.root_ids,root.global_outline_color,root.global_fill_color,root.background_color,language_name)

#_______________Save Functions___________________
def save_letter(language: str, name_letter: str, letter: l.Letter) -> None:
    #BASE WRITTEN BY AI
    letter = to_plain_letter(letter)
    directory = f"languages/{language}/letters"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{name_letter}.json"
    with open(file_path, 'w') as file:
        json.dump(letter, file, default=lambda o: o.__dict__, indent=6)
    exporter.export_preview_img(language,name_letter,letter)

def save_positioning(language: str, name_letter_space: str, letter_spaces: list, is_template:bool=True) -> None:
    #Inspired by save_letter
    reduced_letter_spaces = []
    for letter_space in letter_spaces:
        reduced_letter_spaces.append(to_reduced_letter_space(letter_space))
    if is_template:
        directory = f"languages/{language}/positioning/templates"
    else:
        directory = f"languages/{language}/positioning/letters"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{name_letter_space}.json"
    with open(file_path, 'w') as file:
        json.dump(reduced_letter_spaces, file, default=lambda o: o.__dict__, indent=6)

def save_writing(language: str, name_writing: str, writing_root: l.WritingRoot) -> None:
    #Inspired by save_letter
    reduced_writing_root = to_reduced_writing_root(writing_root,language)

    directory = f"languages/{language}/texts"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{name_writing}.json"
    with open(file_path, 'w') as file:
        json.dump(reduced_writing_root, file, default=lambda o: o.__dict__, indent=6)

#_____________________Load Functions________________________
def load_groups(language:str) -> None:
    global all_groups
    file_path = f"languages/{language}/config.txt"
    all_groups = []
    with open(file_path,"r") as file:
        stage = None
        for line in file:
            line = line.rstrip()
            if line == "groups":
                stage = "GROUP"
            elif line == "end_groups":
                stage = None
            elif stage == "GROUP":
                name,color,parent = line.split(":")
                all_groups.append(l.Group(name,color,parent))

def load_letter(language: str, name_letter: str, use_editor_versions: bool = False) -> l.Letter:
    #Written by Copilot, Modified by me
    global new_language
    file_path = f"languages/{language}/letters/{name_letter}.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    new_language = language
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    letter = l.Letter()
    if "groups" in data:
        letter.groups = data["groups"]
    for segment_data in data['segments']:
        segment = l.Segment()
        segment.name = segment_data['name']
        if 'is_empty' in segment_data:
            segment.is_empty = segment_data['is_empty']
        for node_data in segment_data['nodes']:
            if use_editor_versions:
                node = l.EditorNode(node_data['x'], node_data['y'])
            else:
                node = l.Node(node_data['x'], node_data['y'])
            segment.nodes.append(node)
        for connector_data in segment_data['connectors']:
            if use_editor_versions:
                connector = l.EditorConnector(connector_data['type'])
            else:
                connector = l.Connector(connector_data['type'])
            if connector_data['type'] == "BEZIER":
                connector.anchors = [l.Node(connector_data['anchors'][0]['x'], connector_data['anchors'][0]['y']),
                                     l.Node(connector_data['anchors'][1]['x'], connector_data['anchors'][1]['y'])]
            if connector_data['type'] == "CIRCLE":
                connector.direction = connector_data["direction"]
            segment.connectors.append(connector)
        letter.segments.append(segment)
    
    return letter

def load_positioning(language: str, name_positioning: str, is_template:bool = True, use_editor_versions: bool = False) -> list:
    #Inspired by load_letter
    global new_language
    if is_template:
        file_path = f"languages/{language}/positioning/templates/{name_positioning}.json"
    else:
        file_path = f"languages/{language}/positioning/letters/{name_positioning}.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    new_language = language
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    slots = []
    for slot_data in data:
        if use_editor_versions:
            slot = l.EditorLetterSpace()
        else:
            slot = l.LetterSpace()
        slot.x = slot_data['x']
        slot.y = slot_data['y']
        slot.width = slot_data['width']
        slot.height = slot_data['height']
        slots.append(slot)
    
    return slots

def load_writing(language: str, name_writing: str) -> l.WritingRoot:
    #Inspired by load_letter
    global new_language
    file_path = f"languages/{language}/texts/{name_writing}.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    new_language = language
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    root = l.WritingRoot()
    root.width = data['width']
    root.height = data['height']
    root.letter_spaces = {}
    for key,reduced_letter_spaace in data['letter_spaces'].items():
        new = l.LetterSpace()
        new.id = data['letter_spaces'][key]['id']
        new.parent_id = data['letter_spaces'][key]['parent_id']
        new.children_ids = data['letter_spaces'][key]['children_ids']
        new.x = data['letter_spaces'][key]['x']
        new.y = data['letter_spaces'][key]['y']
        new.global_x = data['letter_spaces'][key]['global_x']
        new.global_y = data['letter_spaces'][key]['global_y']
        new.width = data['letter_spaces'][key]['width']
        new.height = data['letter_spaces'][key]['height']
        if data['letter_spaces'][key]['has_a_letter']:
            new.letter = load_letter(data['letter_spaces'][key]['language'],data['letter_spaces'][key]['letter_name'])
        new.letter_name = data['letter_spaces'][key]['letter_name']
        new.letter_size = data['letter_spaces'][key]['letter_size']
        new.outline_color_mode = data['letter_spaces'][key]['outline_color_mode']
        new.fill_color_mode = data['letter_spaces'][key]['fill_color_mode']
        new.custom_outline_color = data['letter_spaces'][key]['custom_outline_color']
        new.custom_fill_color = data['letter_spaces'][key]['custom_fill_color']
        new.letter_width = data['letter_spaces'][key]['letter_width']
        root.letter_spaces[int(key)] = new
    root.root_ids = data['root_ids']
    root.global_outline_color = data['global_outline_color']
    root.global_fill_color = data['global_fill_color']
    root.background_color = data['background_color']
    l.id_counter = max(root.letter_spaces.keys()) + 1
    
    return root

#___________________Other Functions_____________________

def create_group(language:str,group:l.Group) -> None:
    file_path = f"languages/{language}/config.txt"
    with open(file_path,"r") as file:
        lines = file.readlines()
    stage = None
    for i,line in enumerate(lines):
        if line == "end_groups":
            lines.insert(i,str(group)+"\n")
            break
    with open(file_path,"w") as file:
        file.writelines(lines)
    load_groups(language)

def delete_group(language:str,group_name:str) -> None:
    file_path = f"languages/{language}/config.txt"
    with open(file_path,"r") as file:
        lines = file.readlines()
    stage = None
    for i,line in enumerate(lines):
        line = line.rstrip()
        if line == "groups":
            stage = "GROUP"
        elif line == "end_groups":
            stage = None
        elif stage == "GROUP":
            if group_name == line.split(":")[0]:
                lines.pop(i)
                break
    with open(file_path,"w") as file:
        file.writelines(lines)
    load_groups(language)

def rename_group(language:str,group_name:str,new_name:str) -> None:
    file_path = f"languages/{language}/config.txt"
    with open(file_path,"r") as file:
        lines = file.readlines()
    stage = None
    for i,line in enumerate(lines):
        line = line.rstrip()
        if line == "groups":
            stage = "GROUP"
        elif line == "end_groups":
            stage = None
        elif stage == "GROUP":
            name,color,parent = line.split(":")
            if group_name == name:
                lines.pop(i)
                lines.insert(i,str(l.Group(new_name,color,parent))+"\n")
                break
    with open(file_path,"w") as file:
        file.writelines(lines)
    load_groups(language)

def create_config_file(language:str):
    file_path = f"languages/{language}/config.txt"
    with open(file_path,"w") as file:
        file.write("groups\nend_groups")
    directory = f"languages/{language}/previews"
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory = f"languages/{language}/texts"
    if not os.path.exists(directory):
        os.makedirs(directory)

