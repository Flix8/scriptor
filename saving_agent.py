import os, json
import letter_core as l
import exporter

new_language = None
all_groups = []
def get_group_obj(name) -> l.Group:
    for group in all_groups:
        if group.name == name:
            return group

class ReducedLetterSpace():
    def __init__(self,x:float=0,y:float=0,width:int=100,height:int=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class SessionData():
    def __init__(self,language,letter_editor=None,letter_config=None,open_frame="EDITOR"):
        self.language = language if language != "" else None
        self.letter_editor = letter_editor if letter_editor != "Unnamed" else None
        self.letter_config = letter_config if letter_config != "Unnamed" else None
        self.open_frame = open_frame

def to_plain_letter(letter: l.Letter) -> l.Letter:
    #Partly written by Copilot
    plain_letter = l.Letter()
    plain_letter.groups = letter.groups
    for segment in letter.segments:
        plain_segment = l.Segment()
        plain_segment.name = segment.name
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

def to_reduced_letter_space(letter_space: l.LetterSpace|l.EditorLetterSpace) -> ReducedLetterSpace:
    return ReducedLetterSpace(letter_space.x,letter_space.y,letter_space.width,letter_space.height)

def save_letter(language: str, name_letter: str, letter: l.Letter) -> None:
    letter = to_plain_letter(letter)
    directory = f"languages/{language}/letters"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{name_letter}.json"
    with open(file_path, 'w') as file:
        json.dump(letter, file, default=lambda o: o.__dict__, indent=6)
    exporter.export_preview_img(language,name_letter,letter)

def save_positioning(language: str, name_letter_space: str, letter_space: l.LetterSpace, is_template:bool=True) -> None:
    letter_space = to_reduced_letter_space(letter_space)
    if is_template:
        directory = f"languages/{language}/positioning/templates"
    else:
        directory = f"languages/{language}/positioning/letters"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{name_letter_space}.json"
    with open(file_path, 'w') as file:
        json.dump(letter_space, file, default=lambda o: o.__dict__, indent=6)

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

def load_letter(language: str, name_letter: str, use_editor_versions: bool = False) -> l.Letter:
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