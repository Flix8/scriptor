import letter_core as letter
from PIL import Image, ImageDraw

def export_preview_img(language,letter_name,letter):
    img = Image.new("RGB", (720,620),"white")
    draw = ImageDraw.Draw(img)
    draw_letter_pil(letter,draw,1,(360,310),"black",4)
    img.save(f"languages/{language}/previews/{letter_name}.png")

def draw_letter_pil(letter:letter.Letter,image,size,pos,color=None,width_letter=None):
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
                    else:
                        draw_bezier(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],image,width_letter,color)
                last_node = node
            if len(segment.nodes) > 1:
                    node = segment.nodes[0]
                    connector = segment.connectors[-1]
                    if connector.type == "LINE":
                        image.line((x + last_node.x*size, y + last_node.y*size, x + node.x*size, y + node.y*size), fill=color, width=width_letter)
                    else:
                        draw_bezier(x,y,last_node,node,size,connector.anchors[0],connector.anchors[1],image,width_letter,color)

def draw_bezier(posx,posy,abs_node1,abs_node2,size,rel_anchor1,rel_anchor2,image,width=3,color="black"):
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