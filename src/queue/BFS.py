import tkinter as tk

root = tk.Tk()
root.title("BFS Visual Super")
root.geometry("900x600")

canvas = tk.Canvas(root, width=900, height=500, bg="white")
canvas.pack()

# ===== GRAPH =====
nodes = {
    "A": (150,200),
    "B": (300,100),
    "C": (300,300),
    "D": (500,50),
    "E": (500,200),
    "F": (500,350),
    "G": (700,200)
}

edges = {
    "A": ["B","C"],
    "B": ["D","E"],
    "C": ["F"],
    "D": [],
    "E": ["G"],
    "F": [],
    "G": []
}

# ===== DRAW EDGES =====
edge_lines = {}
for n, neighs in edges.items():
    x1, y1 = nodes[n]
    for nn in neighs:
        x2, y2 = nodes[nn]
        line = canvas.create_line(x1,y1,x2,y2,width=2)
        edge_lines[(n,nn)] = line

# ===== DRAW NODES =====
circles = {}
for n,(x,y) in nodes.items():
    c = canvas.create_oval(x-30,y-30,x+30,y+30, fill="lightgray")
    t = canvas.create_text(x,y,text=n,font=("Arial",14,"bold"))
    circles[n] = c

# ===== QUEUE VISUAL =====
queue_visual = []

def draw_queue():
    for box in queue_visual:
        canvas.delete(box)
    queue_visual.clear()

    for i, item in enumerate(queue):
        x = 200 + i*60
        rect = canvas.create_rectangle(x, 450, x+50, 490, fill="lightblue")
        txt = canvas.create_text(x+25, 470, text=item)
        queue_visual.append(rect)
        queue_visual.append(txt)

# ===== BFS STATE =====
visited = set()
queue = []
running = False
speed = 800

def bfs_step():
    global running

    if not running:
        return

    if not queue:
        canvas.create_text(450, 520, text="SELESAI BFS!", font=("Arial",16))
        return

    current = queue.pop(0)

    # Node aktif
    canvas.itemconfig(circles[current], fill="yellow")

    def process():
        canvas.itemconfig(circles[current], fill="green")

        for neigh in edges[current]:
            if neigh not in visited:
                visited.add(neigh)
                queue.append(neigh)

                # highlight edge
                canvas.itemconfig(edge_lines[(current, neigh)], fill="red", width=3)

        draw_queue()
        root.after(speed, bfs_step)

    root.after(500, process)

def start():
    global running, queue, visited

    queue = ["A"]
    visited = {"A"}
    running = True

    draw_queue()
    bfs_step()

def reset():
    global queue, visited, running

    queue = []
    visited = set()
    running = False

    for c in circles.values():
        canvas.itemconfig(c, fill="lightgray")

    for e in edge_lines.values():
        canvas.itemconfig(e, fill="black", width=2)

    draw_queue()

def set_speed(val):
    global speed
    speed = int(val)

# ===== CONTROL =====
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Start BFS", command=start).grid(row=0,column=0,padx=10)
tk.Button(frame, text="Reset", command=reset).grid(row=0,column=1,padx=10)

tk.Label(frame, text="Speed").grid(row=0,column=2)
tk.Scale(frame, from_=200, to=1500, orient="horizontal", command=set_speed).grid(row=0,column=3)

root.mainloop()