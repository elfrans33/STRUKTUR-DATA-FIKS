import tkinter as tk

root = tk.Tk()
root.title("Antrian Rumah Sakit (Priority Queue)")
root.geometry("800x400")

canvas = tk.Canvas(root, width=800, height=300, bg="white")
canvas.pack()

# Data
queue = []
colors = {0: "red", 1: "orange", 2: "green"}
labels = {0: "Kritis", 1: "Darurat", 2: "Ringan"}

# Posisi antrian
queue_pos = [150, 250, 350, 450, 550]

# Gambar dokter
canvas.create_rectangle(650, 100, 750, 200, fill="gray")
canvas.create_text(700, 210, text="DOKTER")

status = canvas.create_text(400, 20, text="Tambahkan pasien", font=("Arial", 12))

# Tambah pasien (enqueue)
def tambah(priority):
    if len(queue) >= 5:
        return

    name = labels[priority]
    y = 60 + len(queue)*40

    rect = canvas.create_rectangle(50, y, 130, y+30, fill=colors[priority])
    text = canvas.create_text(90, y+15, text=name)

    queue.append({"priority": priority, "rect": rect, "text": text})

    move_to_queue(len(queue)-1)

# Animasi masuk antrian
def move_to_queue(i):
    target_x = queue_pos[i]
    item = queue[i]

    def step():
        x1, _, _, _ = canvas.coords(item["rect"])
        if x1 < target_x:
            canvas.move(item["rect"], 5, 0)
            canvas.move(item["text"], 5, 0)
            root.after(20, step)

    step()

# Proses pasien (priority)
def proses():
    if not queue:
        return

    canvas.itemconfig(status, text="Memilih pasien prioritas...")

    # Urutkan berdasarkan prioritas
    queue.sort(key=lambda x: x["priority"])

    # Ambil pasien prioritas tertinggi
    item = queue.pop(0)

    canvas.itemconfig(status, text="Pasien diproses...")

    def move():
        x1, _, _, _ = canvas.coords(item["rect"])
        if x1 < 650:
            canvas.move(item["rect"], 5, 0)
            canvas.move(item["text"], 5, 0)
            root.after(20, move)
        else:
            canvas.delete(item["rect"])
            canvas.delete(item["text"])
            canvas.itemconfig(status, text="Selesai melayani pasien")
            geser_antrian()

    move()

# Geser antrian setelah dequeue
def geser_antrian():
    for i, item in enumerate(queue):
        target_x = queue_pos[i]

        def move(item=item, target_x=target_x):
            def step():
                x1, _, _, _ = canvas.coords(item["rect"])
                if x1 > target_x:
                    canvas.move(item["rect"], -5, 0)
                    canvas.move(item["text"], -5, 0)
                    root.after(20, step)
            step()

        move()

# Tombol
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Pasien Kritis", command=lambda: tambah(0)).grid(row=0, column=0, padx=10)
tk.Button(frame, text="Pasien Darurat", command=lambda: tambah(1)).grid(row=0, column=1, padx=10)
tk.Button(frame, text="Pasien Ringan", command=lambda: tambah(2)).grid(row=0, column=2, padx=10)

tk.Button(frame, text="Proses Pasien", command=proses).grid(row=0, column=3, padx=10)

root.mainloop()