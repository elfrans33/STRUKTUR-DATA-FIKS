import tkinter as tk
import random

# ===== SETUP =====
root = tk.Tk()
root.title("Simulasi Loket Bandara (Queue Real-Life)")
root.geometry("900x600")

canvas = tk.Canvas(root, width=900, height=500, bg="white")
canvas.pack()

# ===== PARAMETER =====
ARRIVAL_CHANCE = 0.3      # peluang penumpang datang tiap tick
SERVICE_TIME = (3, 6)     # waktu layanan (detik)
TICK = 1000               # 1 detik

# ===== DATA =====
queue = []
servers = [None, None, None]  # 3 loket
waiting_times = []
time = 0
served = 0

# ===== VISUAL =====
queue_pos = [100 + i*60 for i in range(8)]

# Loket
for i in range(3):
    x = 600 + i*90
    canvas.create_rectangle(x, 100, x+70, 180, fill="gray")
    canvas.create_text(x+35, 190, text=f"Loket {i+1}")

status = canvas.create_text(450, 20, text="Simulasi dimulai...", font=("Arial", 12))
stat_text = canvas.create_text(450, 470, text="", font=("Arial", 12))

# ===== PENUMPANG =====
class Passenger:
    def __init__(self):
        self.arrival_time = time
        self.rect = canvas.create_oval(20, 300, 50, 330, fill="blue")

# ===== ANIMASI MASUK ANTRIAN =====
def move_to_queue(p, index):
    target_x = queue_pos[index]

    def step():
        x1, _, _, _ = canvas.coords(p.rect)
        if x1 < target_x:
            canvas.move(p.rect, 5, 0)
            root.after(20, step)
    step()

# ===== GESER ANTRIAN =====
def shift_queue():
    for i, p in enumerate(queue):
        target_x = queue_pos[i]

        def move(p=p, target_x=target_x):
            def step():
                x1, _, _, _ = canvas.coords(p.rect)
                if x1 > target_x:
                    canvas.move(p.rect, -5, 0)
                    root.after(20, step)
            step()
        move()

# ===== PROSES KE LOKET =====
def move_to_server(p, server_index):
    target_x = 600 + server_index*90

    def step():
        x1, _, _, _ = canvas.coords(p.rect)
        if x1 < target_x:
            canvas.move(p.rect, 5, -2)
            root.after(20, step)
        else:
            start_service(p, server_index)
    step()

# ===== LAYANAN =====
def start_service(p, server_index):
    global served

    service_duration = random.randint(*SERVICE_TIME)

    def finish():
        global served
        canvas.delete(p.rect)
        servers[server_index] = None

        wait = time - p.arrival_time
        waiting_times.append(wait)
        served += 1

    root.after(service_duration * 1000, finish)

# ===== UPDATE SIMULASI =====
def update():
    global time

    time += 1

    # R1: penumpang datang
    if random.random() < ARRIVAL_CHANCE:
        p = Passenger()
        queue.append(p)
        move_to_queue(p, len(queue)-1)

    # R2: assign ke loket
    for i in range(len(servers)):
        if servers[i] is None and queue:
            p = queue.pop(0)
            servers[i] = p
            move_to_server(p, i)
            shift_queue()

    # Statistik
    avg_wait = sum(waiting_times)/len(waiting_times) if waiting_times else 0
    canvas.itemconfig(stat_text,
        text=f"Served: {served} | Avg Wait: {avg_wait:.2f} detik | Queue: {len(queue)}")

    root.after(TICK, update)

# ===== START =====
def start():
    update()

tk.Button(root, text="Mulai Simulasi", command=start).pack(pady=10)

root.mainloop()