import tkinter as tk
import math

root = tk.Tk()
root.title("Hot Potato (Aman)")

canvas = tk.Canvas(root, width=500, height=500)
canvas.pack()

# Data pemain
players = ["A", "B", "C", "D", "E"]
circles = []

center_x, center_y = 250, 250
radius = 150

# Buat lingkaran pemain
for i, p in enumerate(players):
    angle = (2 * math.pi / len(players)) * i
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    
    circle = canvas.create_oval(x-20, y-20, x+20, y+20, fill="lightblue")
    text = canvas.create_text(x, y, text=p)
    circles.append((circle, text))

# Bola
ball = canvas.create_oval(240, 240, 260, 260, fill="red")

index = 0
counter = 0
limit = 5   # jumlah oper sebelum eliminasi

running = False

def move_ball():
    global index, counter, running

    if not running:
        return

    if len(circles) <= 1:
        canvas.create_text(250, 450, text="Pemenang!", font=("Arial", 16))
        return

    # AMAN: jaga index
    index = index % len(circles)

    x1, y1, x2, y2 = canvas.coords(circles[index][0])
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    
    canvas.coords(ball, cx-10, cy-10, cx+10, cy+10)

    counter += 1

    # Jika sudah limit → eliminasi
    if counter >= limit:
        eliminate()
        counter = 0

    index = (index + 1) % len(circles)

    root.after(500, move_ball)

def eliminate():
    global index

    if len(circles) <= 1:
        return

    # AMAN: sesuaikan index sebelum hapus
    index = (index - 1) % len(circles)

    circle, text = circles.pop(index)
    canvas.delete(circle)
    canvas.delete(text)

    # AMAN: reset index
    if len(circles) > 0:
        index = index % len(circles)

def start():
    global running
    running = True
    move_ball()

btn = tk.Button(root, text="Start Game", command=start)
btn.pack(pady=10)

root.mainloop()