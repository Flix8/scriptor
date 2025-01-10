import os, json
import letter_core as l

new_language = None

def to_plain_letter(letter: l.Letter) -> l.Letter:
    #Written by Copilot
    plain_letter = l.Letter()
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
            plain_segment.connectors.append(plain_connector)
        plain_letter.segments.append(plain_segment)
    return plain_letter

def save_letter(language: str, name_letter: str, letter: l.Letter) -> None:
    letter = to_plain_letter(letter)
    directory = f"languages/{language}/letters"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{name_letter}.json"
    with open(file_path, 'w') as file:
        json.dump(letter, file, default=lambda o: o.__dict__, indent=6)

def load_letter(language: str, name_letter: str, use_editor_versions: bool = False) -> l.Letter:
    global new_language
    file_path = f"languages/{language}/letters/{name_letter}.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    new_language = language
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    letter = l.Letter()
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
            segment.connectors.append(connector)
        letter.segments.append(segment)
    
    return letter