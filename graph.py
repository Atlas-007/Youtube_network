import ChannelNetwork
import os
import tkinter as tk
import random
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO
import requests
import math
import gui

inputs = gui.launch_gui()
Number_of_Nodes = inputs["channels"]
Number_of_commenters_pull = inputs["commenters"]
Max_subscriptions_per_commenter = inputs["subs_per_com"]

ChannelName = inputs["main_channel"] # Change to your desired channel name

api_key = os.environ.get("YT_API_KEY") # set your YouTube Data API key in environment variable: export YT_API_KEY="your_key_here"
if not api_key:
    raise ValueError("Please set the YT_API_KEY environment variable")


x = ChannelNetwork.DataCollect(api_key, Number_of_Nodes, Number_of_commenters_pull, Max_subscriptions_per_commenter, ChannelName)


class Node:
    SCREEN_SIZE = 1000
    existing_nodes = []

    def __init__(self, data):
        self.channel_id = data["channel_id"]
        self.title = data.get("title", "")
        self.titlelen = len(self.title)
        self.connections = data.get("count", 0)
        self.profilePic = data.get("profile_image_url", "")
        self.tk_img = None


        paddingx = (self.radius() + (self.titlelen * 3))
        paddingy = self.radius() + 10

        self.x = random.randint(0 + paddingx, self.SCREEN_SIZE - paddingx)
        self.y = random.randint(0 + paddingy, self.SCREEN_SIZE - paddingy)

        while (self._check_overlap()):
            self.x = random.randint(0 + paddingx, self.SCREEN_SIZE - paddingx)
            self.y = random.randint(0 + paddingy, self.SCREEN_SIZE - paddingy)

        Node.existing_nodes.append(self)

    def pos(self):
        return self.x, self.y

    
    def radius(self, min_radius=4, scale=2, maxRadius=40):
        if min_radius + self.connections * scale < maxRadius:
            return min_radius + self.connections * scale
        else:
            return maxRadius

    def _check_overlap(self):
        for node in Node.existing_nodes:
            distance = math.hypot(self.x - node.x, self.y - node.y)
            if distance < self.radius() + node.radius():
                return True
        return False

    
    
class Edge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2


nodes = [Node(data) for data in x]




central_name = ChannelName
central_node = None
for node in nodes:
    if node.title == central_name:
        central_node = node
        break

if central_node is None:
    central_node = nodes[0] 



root = tk.Tk()
root.title("Graph")


canvas = tk.Canvas(root, width=1000, height=1000, bg="white")
canvas.pack()

# Draw edges
for node in nodes:
    if node == central_node:
        continue  
    canvas.create_line(
        central_node.x, central_node.y,
        node.x, node.y,
        fill="gray", width= (2*node.connections)/10 if node.connections < 50 else 10
    )


# Draw nodes
for node in nodes:
    x, y = node.pos()
    r = node.radius()


    canvas.create_oval(x - r, y - r, x + r, y + r, fill="blue")
    canvas.create_text(x - node.titlelen * 3, y + r + 10, text=node.title, anchor="w")

    # Load profile picture from URL
    response = requests.get(node.profilePic)
    img_data = response.content
    img = Image.open(BytesIO(img_data)).convert("RGBA")

    # add a mask to make it circular and fit the node size
    img = img.resize((r*2, r*2))
    mask = Image.new("L", (r*2, r*2), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, r*2, r*2), fill=255)
    img.putalpha(mask)

    # Convert to Tkinter PhotoImage
    tk_img = ImageTk.PhotoImage(img)
    node.tk_img = tk_img  
    canvas.create_image(x, y, image=tk_img)


root.mainloop()