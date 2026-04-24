import tkinter as tk
from collections import deque

# Setup window
root = tk.Tk()
root.title("Simulasi Antrian Printer (FIFO)")
root.geometry("800x400")

canvas = tk.Canvas(root, width=800, height=300, bg="white")
canvas.pack()

# Queue data
queue = deque()
doc_objects = []

# Posisi antrian
queue_x_positions = [250, 350, 450, 550]

# Gambar printer
printer = canvas.create_rectangle(650, 120, 750, 200, fill="gray")
canvas.create_text(700, 210, text="PRINTER")

status_text = canvas.create_text(400, 20, text="Klik 'Tambah Dokumen'", font=("Arial", 12))

# Fungsi tambah dokumen
def tambah_dokumen():
    if len(queue) >= 4:
        return
    
    doc_name = f"Doc{len(queue)+1}"
    queue.append(doc_name)
    
    y_pos = 50 + len(queue)*40
    rect = canvas.create_rectangle(50, y_pos, 130, y_pos+30, fill="lightblue")
    text = canvas.create_text(90, y_pos+15, text=doc_name)
    
    doc_objects.append((rect, text))
    
    move_to_queue(len(doc_objects)-1)

# Animasi ke antrian
def move_to_queue(index):
    rect, text = doc_objects[index]
    target_x = queue_x_positions[index]
    
    def step():
        x1, _, _, _ = canvas.coords(rect)
        if x1 < target_x:
            canvas.move(rect, 5, 0)
            canvas.move(text, 5, 0)
            root.after(20, step)
    
    step()

# Proses cetak (FIFO)
def proses_cetak():
    if not queue:
        return
    
    canvas.itemconfig(status_text, text="Mencetak dokumen...")
    
    rect, text = doc_objects.pop(0)
    queue.popleft()
    
    def step():
        x1, _, _, _ = canvas.coords(rect)
        if x1 < 650:
            canvas.move(rect, 5, 0)
            canvas.move(text, 5, 0)
            root.after(20, step)
        else:
            canvas.delete(rect)
            canvas.delete(text)
            canvas.itemconfig(status_text, text="Selesai mencetak")
            geser_antrian()
    
    step()

# Geser antrian setelah dequeue
def geser_antrian():
    for i, (rect, text) in enumerate(doc_objects):
        target_x = queue_x_positions[i]
        
        def move(rect=rect, text=text, target_x=target_x):
            def step():
                x1, _, _, _ = canvas.coords(rect)
                if x1 > target_x:
                    canvas.move(rect, -5, 0)
                    canvas.move(text, -5, 0)
                    root.after(20, step)
            step()
        
        move()

# Tombol
frame = tk.Frame(root)
frame.pack(pady=10)

btn_add = tk.Button(frame, text="Tambah Dokumen", command=tambah_dokumen)
btn_add.grid(row=0, column=0, padx=10)

btn_print = tk.Button(frame, text="Cetak (FIFO)", command=proses_cetak)
btn_print.grid(row=0, column=1, padx=10)

root.mainloop()