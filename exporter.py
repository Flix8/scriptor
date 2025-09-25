import letter_core as letter
from PIL import Image, ImageDraw
from math import sin,cos,radians
#MOSTLY WRITTEN BY MYSELF. ONLY SINGLE LINES THAT WERE SUGGESTED BY AI.
#What this does: Exporting letters and texts as pngs with Pillow.

def export_preview_img(language,letter_name,letter):
    img = Image.new("RGB", (720,620),"white")
    draw = ImageDraw.Draw(img)
    draw_letter_pil(letter,draw,1,(360,310),"black",4)
    img.save(f"languages/{language}/previews/{letter_name}.png")

def export_write(path,writing_root:letter.WritingRoot):
    if not writing_root.transparent_background:
        img = Image.new("RGB", (writing_root.width,writing_root.height),writing_root.background_color)
    else:
        img = Image.new("RGBA", (writing_root.width,writing_root.height),(0,0,0,0))
    draw = ImageDraw.Draw(img)
    for child_id in writing_root.root_ids:
        recursive_slots_draw(draw,writing_root,writing_root.get_letter_space_with_id(child_id),letter.Node(writing_root.width//2,writing_root.height//2))
    img.save(path)

def recursive_slots_draw(image,writing_root:letter.WritingRoot,slot:letter.LetterSpace,center:letter.Node=letter.Node(0,0)):
    #Draw self
    if slot.letter is not None:
        draw_letter_polygon_pil(slot.letter,image,slot.letter_size,letter.Node(center.x+slot.x,center.y+slot.y),writing_root.global_outline_color if slot.outline_color_mode == "GLOBAL" else slot.custom_outline_color,slot.letter_width,writing_root.global_fill_color if slot.fill_color_mode == "GLOBAL" else slot.custom_fill_color,writing_root.background_color,writing_root.transparent_background)
    #Draw children
    for child_id in slot.children_ids:
        recursive_slots_draw(image,writing_root,writing_root.get_letter_space_with_id(child_id),letter.Node(center.x+slot.x,center.y+slot.y))

#_______________Drawing Functions with Pillow_________________________
def draw_letter_pil(letter:letter.Letter,image,size,pos,color=None,width_letter=None):
        #Only explanation, what functions there are in Pillow. Written myself.
        x,y = pos
        for segment in letter.segments:
            last_node = None
            for i,node in enumerate(segment.nodes):
                if len(segment.nodes) == 1:
                    break
                if last_node != None:
                    connector = segment.connectors[i-1]
                    if connector.type == "LINE":
                        image.line((x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size), fill=color, width=width_letter)
                    elif connector.type == "BEZIER":
                        draw_bezier_pil(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],image,width_letter,color)
                    else:
                        draw_half_circle_pil(x,y,last_node,node,size,connector.direction,image,width_letter,color)
                last_node = node
            if len(segment.nodes) > 1:
                    node = segment.nodes[0]
                    connector = segment.connectors[-1]
                    if connector.type == "LINE":
                        image.line((x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size), fill=color, width=width_letter)
                    elif connector.type == "BEZIER":
                        draw_bezier_pil(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],image,width_letter,color)
                    else:
                        draw_half_circle_pil(x,y,last_node,node,size,connector.direction,image,width_letter,color)

def draw_letter_polygon_pil(let:letter.Letter,image,size:float,center:letter.Node,color_letter:str="black",width_letter:int=1,fill_color:str="white",empty_color:str="#525252",transparent_background:bool=False):
    x,y = center.x,center.y
    for segment_index, segment in enumerate(let.segments):
        polygon_positions = []
        last_node = None

        for i,node in enumerate(segment.nodes):
            if len(segment.nodes) == 1: break
            if last_node != None:
                connector = segment.connectors[i-1]
                if connector.type == "BEZIER":
                    polygon_positions += letter.get_bezier_positions(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1])
                elif connector.type == "CIRCLE":
                    polygon_positions += letter.get_half_circle_positions(x,y,last_node,node,size,connector.direction)
            polygon_positions += [x + node.x*size, y + node.y*size]
            last_node = node
        if len(segment.nodes) > 1:
                node = segment.nodes[0]
                connector = segment.connectors[-1]
                if connector.type == "BEZIER":
                    polygon_positions += letter.get_bezier_positions(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1])
                elif connector.type == "CIRCLE":
                    polygon_positions += letter.get_half_circle_positions(x,y,last_node,node,size,connector.direction)
        if not segment.is_empty:
            image.polygon(polygon_positions,width=width_letter,outline=color_letter,fill=fill_color)
        elif not transparent_background:
            image.polygon(polygon_positions,width=width_letter,outline=color_letter,fill=empty_color)
        else:
            image.polygon(polygon_positions,width=width_letter,outline=color_letter,fill=(0,0,0,0))


def draw_bezier_pil(posx,posy,abs_node1,abs_node2,size,rel_anchor1,rel_anchor2,image,width=3,color="black"):
    #Modified code from: https://stackoverflow.com/a/50302363
    node1 = letter.Node(posx + abs_node1.x * size,posy + abs_node1.y * size)
    node2 = letter.Node(posx + abs_node2.x * size,posy + abs_node2.y * size)
    x_start = node1.x
    y_start = node1.y
    anchor1 = letter.Node(rel_anchor1.x * size + node1.x,rel_anchor1.y * size + node1.y)
    anchor2 = letter.Node(rel_anchor2.x * size + node2.x,rel_anchor2.y * size + node2.y)
    n = 50
    for i in range(n):
        t = i / n
        x = (node1.x * (1-t)**3 + anchor1.x * 3 * t * (1-t)**2 + anchor2.x * 3 * t**2 * (1-t) + node2.x * t**3)
        y = (node1.y * (1-t)**3 + anchor1.y * 3 * t * (1-t)**2 + anchor2.y * 3 * t**2 * (1-t) + node2.y * t**3)

        image.line((x, y, x_start, y_start),fill=color, width=width)
        x_start = x
        y_start = y

def draw_half_circle_pil(posx,posy,abs_node1,abs_node2,size,direction,image,width=3,color="black"):
    node1 = letter.Node(abs_node1.x * size,abs_node1.y * size)
    node2 = letter.Node(abs_node2.x * size,abs_node2.y * size)
    offset = node1 + (node2-node1)/2
    x_start = node1.x - offset.x
    y_start = node1.y - offset.y
    n = 50
    for i in range(n):
        x = x_start * cos(radians(180/n*direction)) - y_start * sin(radians(180/n*direction))
        y = y_start * cos(radians(180/n*direction)) + x_start * sin(radians(180/n*direction))
        image.line((x + offset.x + posx, y + offset.y + posy, x_start + offset.x + posx, y_start + offset.y + posy),fill=color, width=width)
        x_start = x
        y_start = y