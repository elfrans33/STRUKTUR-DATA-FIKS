import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

# ─────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────
BG        = "#0f1117"
PANEL     = "#1a1d2e"
ACCENT    = "#7c3aed"
ACCENT2   = "#06b6d4"
SUCCESS   = "#10b981"
WARNING   = "#f59e0b"
TEXT      = "#e2e8f0"
SUBTEXT   = "#94a3b8"
BORDER    = "#2d3148"
LIGHT_SQ  = "#c9a96e"
DARK_SQ   = "#7d5a3c"
QUEEN_CLR = "#f43f5e"
KNIGHT_CLR= "#06b6d4"
VISITED   = "#7c3aed"


# ═══════════════════════════════════════════════════════════════
#  1. N-QUEENS  (backtracking)
# ═══════════════════════════════════════════════════════════════
def solve_nqueens(n):
    """Return list of column-placements for each row, or None."""
    board = [-1] * n

    def is_safe(row, col):
        for r in range(row):
            c = board[r]
            if c == col or abs(c - col) == abs(r - row):
                return False
        return True

    def backtrack(row):
        if row == n:
            return True
        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                if backtrack(row + 1):
                    return True
                board[row] = -1
        return False

    if backtrack(0):
        return board
    return None


# ═══════════════════════════════════════════════════════════════
#  2. KNIGHT'S TOUR  (Warnsdorff heuristic + backtracking)
# ═══════════════════════════════════════════════════════════════
MOVES = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]

def solve_knights_tour(n, start_row, start_col):
    board = [[-1]*n for _ in range(n)]
    board[start_row][start_col] = 0

    def degree(r, c):
        cnt = 0
        for dr, dc in MOVES:
            nr, nc = r+dr, c+dc
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == -1:
                cnt += 1
        return cnt

    def backtrack(r, c, move_num):
        if move_num == n*n:
            return True
        neighbors = []
        for dr, dc in MOVES:
            nr, nc = r+dr, c+dc
            if 0 <= nr < n and 0 <= nc < n and board[nr][nc] == -1:
                neighbors.append((degree(nr, nc), nr, nc))
        neighbors.sort()
        for _, nr, nc in neighbors:
            board[nr][nc] = move_num
            if backtrack(nr, nc, move_num+1):
                return True
            board[nr][nc] = -1
        return False

    if backtrack(start_row, start_col, 1):
        return board
    return None


# ═══════════════════════════════════════════════════════════════
#  3. KNAPSACK  (recursive subset-sum style)
# ═══════════════════════════════════════════════════════════════
def solve_knapsack(weights, target):
    """Return a list of chosen weights that sum to exactly target, or None."""
    chosen = []

    def backtrack(idx, remaining):
        if remaining == 0:
            return True
        if idx >= len(weights) or remaining < 0:
            return False
        # include
        chosen.append(weights[idx])
        if backtrack(idx+1, remaining - weights[idx]):
            return True
        chosen.pop()
        # skip
        if backtrack(idx+1, remaining):
            return True
        return False

    if backtrack(0, target):
        return chosen
    return None


# ═══════════════════════════════════════════════════════════════
#  GUI  APPLICATION
# ═══════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algoritma Rekursif & Backtracking")
        self.configure(bg=BG)
        self.geometry("980x700")
        self.resizable(True, True)
        self._build_ui()

    # ── helpers ──────────────────────────────────────────────
    def _label(self, parent, text, size=11, bold=False, color=TEXT, **kw):
        font = ("Consolas", size, "bold" if bold else "normal")
        return tk.Label(parent, text=text, font=font,
                        bg=kw.pop("bg", PANEL), fg=color, **kw)

    def _btn(self, parent, text, cmd, color=ACCENT, **kw):
        b = tk.Button(parent, text=text, command=cmd,
                      font=("Consolas", 10, "bold"),
                      bg=color, fg="white", relief="flat",
                      activebackground=color, activeforeground="white",
                      cursor="hand2", padx=14, pady=6, **kw)
        b.bind("<Enter>", lambda e: b.config(bg=self._lighten(color)))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    @staticmethod
    def _lighten(hex_color):
        r = min(255, int(hex_color[1:3], 16)+30)
        g = min(255, int(hex_color[3:5], 16)+30)
        b = min(255, int(hex_color[5:7], 16)+30)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _entry(self, parent, width=8, **kw):
        e = tk.Entry(parent, font=("Consolas", 11),
                     bg="#252840", fg=TEXT, insertbackground=TEXT,
                     relief="flat", highlightthickness=1,
                     highlightbackground=BORDER,
                     highlightcolor=ACCENT, width=width, **kw)
        return e

    def _section(self, notebook, title):
        frame = tk.Frame(notebook, bg=BG)
        notebook.add(frame, text=f"  {title}  ")
        return frame

    # ── main UI ──────────────────────────────────────────────
    def _build_ui(self):
        # ── header ──
        hdr = tk.Frame(self, bg=PANEL, height=56)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚙  ALGORITMA REKURSIF & BACKTRACKING",
                 font=("Consolas", 13, "bold"),
                 bg=PANEL, fg=ACCENT).pack(side="left", padx=20, pady=14)
        tk.Label(hdr, text="Python · Tugas Struktur Data",
                 font=("Consolas", 9), bg=PANEL, fg=SUBTEXT).pack(side="right", padx=20)

        # separator
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

        # ── notebook ──
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=PANEL, foreground=SUBTEXT,
                        font=("Consolas", 10, "bold"),
                        padding=[14, 8], borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_nqueens(self._section(nb, "♛  N-Queens"))
        self._build_knights(self._section(nb, "♞  Knight's Tour"))
        self._build_knapsack(self._section(nb, "🎒  Knapsack"))

    # ══════════════════════════════════════════════════════════
    #  TAB 1 – N-QUEENS
    # ══════════════════════════════════════════════════════════
    def _build_nqueens(self, frame):
        # left panel
        left = tk.Frame(frame, bg=PANEL, width=240)
        left.pack(side="left", fill="y", padx=(12,0), pady=12)
        left.pack_propagate(False)

        self._label(left, "N-QUEENS SOLVER", 12, True, ACCENT).pack(pady=(18,4), padx=14, anchor="w")
        self._label(left,
            "Tempatkan N ratu di papan N×N\n"
            "sehingga tidak ada dua ratu\n"
            "yang saling menyerang.",
            9, color=SUBTEXT).pack(padx=14, anchor="w")

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14, pady=12)

        self._label(left, "Ukuran Papan (N) :").pack(padx=14, anchor="w")
        self.nq_entry = self._entry(left, width=6)
        self.nq_entry.insert(0, "8")
        self.nq_entry.pack(padx=14, pady=(4,12), anchor="w")

        self._btn(left, "▶  Cari Solusi", self._run_nqueens, ACCENT).pack(padx=14, fill="x")

        self.nq_status = self._label(left, "", 9, color=SUBTEXT)
        self.nq_status.pack(padx=14, pady=(10,0), anchor="w")

        # canvas area
        right = tk.Frame(frame, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        self._label(right, "Visualisasi Papan", 10, True, bg=BG).pack(anchor="w", pady=(0,6))
        self.nq_canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        self.nq_canvas.pack(fill="both", expand=True)

    def _run_nqueens(self):
        try:
            n = int(self.nq_entry.get())
            if n < 1 or n > 20:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan angka antara 1–20")
            return

        self.nq_status.config(text="Mencari solusi...", fg=WARNING)
        self.update()
        t0 = time.time()
        sol = solve_nqueens(n)
        elapsed = time.time() - t0

        if sol:
            self.nq_status.config(
                text=f"✔ Solusi ditemukan  ({elapsed:.4f}s)", fg=SUCCESS)
            self._draw_nqueens(n, sol)
        else:
            self.nq_status.config(text="✘ Tidak ada solusi", fg=QUEEN_CLR)
            self.nq_canvas.delete("all")

    def _draw_nqueens(self, n, board):
        c = self.nq_canvas
        c.delete("all")
        c.update()
        W, H = c.winfo_width(), c.winfo_height()
        margin = 20
        cell = min((W - 2*margin) // n, (H - 2*margin) // n)
        ox = (W - cell*n) // 2
        oy = (H - cell*n) // 2

        for r in range(n):
            for col in range(n):
                color = LIGHT_SQ if (r+col) % 2 == 0 else DARK_SQ
                x1, y1 = ox + col*cell, oy + r*cell
                c.create_rectangle(x1, y1, x1+cell, y1+cell,
                                   fill=color, outline="")
                if board[r] == col:
                    pad = cell * 0.12
                    c.create_oval(x1+pad, y1+pad,
                                  x1+cell-pad, y1+cell-pad,
                                  fill=QUEEN_CLR, outline="#fff", width=2)
                    fs = max(8, int(cell * 0.45))
                    c.create_text(x1+cell//2, y1+cell//2,
                                  text="♛", fill="white",
                                  font=("Arial", fs))

        # row/col labels
        for i in range(n):
            fs = max(7, int(cell * 0.28))
            c.create_text(ox + i*cell + cell//2, oy - 10,
                          text=str(i+1), fill=SUBTEXT,
                          font=("Consolas", fs))
            c.create_text(ox - 10, oy + i*cell + cell//2,
                          text=str(i+1), fill=SUBTEXT,
                          font=("Consolas", fs))

    # ══════════════════════════════════════════════════════════
    #  TAB 2 – KNIGHT'S TOUR
    # ══════════════════════════════════════════════════════════
    def _build_knights(self, frame):
        left = tk.Frame(frame, bg=PANEL, width=240)
        left.pack(side="left", fill="y", padx=(12,0), pady=12)
        left.pack_propagate(False)

        self._label(left, "KNIGHT'S TOUR", 12, True, ACCENT2).pack(pady=(18,4), padx=14, anchor="w")
        self._label(left,
            "Kuda mengunjungi setiap petak\n"
            "tepat satu kali menggunakan\n"
            "backtracking rekursif.",
            9, color=SUBTEXT).pack(padx=14, anchor="w")

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14, pady=12)

        self._label(left, "Ukuran Papan (N) :").pack(padx=14, anchor="w")
        self.kt_n = self._entry(left, width=6)
        self.kt_n.insert(0, "6")
        self.kt_n.pack(padx=14, pady=(4,8), anchor="w")

        self._label(left, "Baris Awal (0-based) :").pack(padx=14, anchor="w")
        self.kt_row = self._entry(left, width=6)
        self.kt_row.insert(0, "0")
        self.kt_row.pack(padx=14, pady=(4,8), anchor="w")

        self._label(left, "Kolom Awal (0-based) :").pack(padx=14, anchor="w")
        self.kt_col = self._entry(left, width=6)
        self.kt_col.insert(0, "0")
        self.kt_col.pack(padx=14, pady=(4,12), anchor="w")

        self._btn(left, "▶  Cari Solusi", self._run_knights, ACCENT2).pack(padx=14, fill="x")

        self.kt_status = self._label(left, "", 9, color=SUBTEXT)
        self.kt_status.pack(padx=14, pady=(10,0), anchor="w")

        right = tk.Frame(frame, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        self._label(right, "Visualisasi Tur Kuda", 10, True, bg=BG).pack(anchor="w", pady=(0,6))
        self.kt_canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        self.kt_canvas.pack(fill="both", expand=True)

    def _run_knights(self):
        try:
            n   = int(self.kt_n.get())
            row = int(self.kt_row.get())
            col = int(self.kt_col.get())
            if n < 1 or n > 8:
                raise ValueError("n")
            if not (0 <= row < n and 0 <= col < n):
                raise ValueError("pos")
        except ValueError as e:
            if "pos" in str(e):
                messagebox.showerror("Input Error",
                    f"Posisi awal harus antara 0 dan {int(self.kt_n.get())-1}")
            else:
                messagebox.showerror("Input Error", "N harus 1–8")
            return

        self.kt_status.config(text="Mencari solusi...", fg=WARNING)
        self.update()
        t0 = time.time()
        sol = solve_knights_tour(n, row, col)
        elapsed = time.time() - t0

        if sol:
            self.kt_status.config(
                text=f"✔ Solusi ditemukan  ({elapsed:.4f}s)", fg=SUCCESS)
            self._draw_knights(n, sol)
        else:
            self.kt_status.config(text="✘ Tidak ada solusi dari posisi ini", fg=QUEEN_CLR)
            self.kt_canvas.delete("all")

    def _draw_knights(self, n, board):
        c = self.kt_canvas
        c.delete("all")
        c.update()
        W, H = c.winfo_width(), c.winfo_height()
        margin = 20
        cell = min((W - 2*margin) // n, (H - 2*margin) // n)
        ox = (W - cell*n) // 2
        oy = (H - cell*n) // 2

        # build move-order list
        order = [(0,0)] * (n*n)
        for r in range(n):
            for cc in range(n):
                order[board[r][cc]] = (r, cc)

        for r in range(n):
            for cc in range(n):
                color = LIGHT_SQ if (r+cc) % 2 == 0 else DARK_SQ
                x1 = ox + cc*cell
                y1 = oy + r*cell
                c.create_rectangle(x1, y1, x1+cell, y1+cell,
                                   fill=color, outline="")
                move_num = board[r][cc]
                # gradient-like coloring for the path
                ratio = move_num / (n*n - 1) if n*n > 1 else 0
                # blend from ACCENT to ACCENT2
                def blend(h1, h2, t):
                    r1,g1,b1 = int(h1[1:3],16),int(h1[3:5],16),int(h1[5:7],16)
                    r2,g2,b2 = int(h2[1:3],16),int(h2[3:5],16),int(h2[5:7],16)
                    return (int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))
                ri,gi,bi = blend(ACCENT, ACCENT2, ratio)
                dot_col = f"#{ri:02x}{gi:02x}{bi:02x}"

                pad = cell * 0.25
                c.create_oval(x1+pad, y1+pad, x1+cell-pad, y1+cell-pad,
                              fill=dot_col, outline="")
                fs = max(6, int(cell * 0.30))
                c.create_text(x1+cell//2, y1+cell//2,
                              text=str(move_num+1), fill="white",
                              font=("Consolas", fs, "bold"))

        # draw path lines
        for i in range(len(order)-1):
            r1,c1 = order[i]
            r2,c2 = order[i+1]
            cx1 = ox + c1*cell + cell//2
            cy1 = oy + r1*cell + cell//2
            cx2 = ox + c2*cell + cell//2
            cy2 = oy + r2*cell + cell//2
            c.create_line(cx1,cy1, cx2,cy2,
                          fill="#ffffff33", width=1, dash=(3,3))

        # start marker
        sr, sc = order[0]
        x1 = ox + sc*cell
        y1 = oy + sr*cell
        fs = max(8, int(cell * 0.45))
        c.create_text(x1+cell//2, y1+cell//2,
                      text="♞", fill="white",
                      font=("Arial", fs))

    # ══════════════════════════════════════════════════════════
    #  TAB 3 – KNAPSACK
    # ══════════════════════════════════════════════════════════
    def _build_knapsack(self, frame):
        left = tk.Frame(frame, bg=PANEL, width=300)
        left.pack(side="left", fill="y", padx=(12,0), pady=12)
        left.pack_propagate(False)

        self._label(left, "KNAPSACK SOLVER", 12, True, WARNING).pack(pady=(18,4), padx=14, anchor="w")
        self._label(left,
            "Temukan kombinasi barang yang\n"
            "totalnya sama dengan target\n"
            "menggunakan rekursi.",
            9, color=SUBTEXT).pack(padx=14, anchor="w")

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14, pady=12)

        self._label(left, "Berat Barang (pisah koma) :").pack(padx=14, anchor="w")
        self.ks_weights = self._entry(left, width=24)
        self.ks_weights.insert(0, "2, 5, 6, 9, 12, 14, 20")
        self.ks_weights.pack(padx=14, pady=(4,8), anchor="w")

        self._label(left, "Target Berat :").pack(padx=14, anchor="w")
        self.ks_target = self._entry(left, width=8)
        self.ks_target.insert(0, "30")
        self.ks_target.pack(padx=14, pady=(4,12), anchor="w")

        self._btn(left, "▶  Cari Solusi", self._run_knapsack, WARNING).pack(padx=14, fill="x")

        self.ks_status = self._label(left, "", 9, color=SUBTEXT)
        self.ks_status.pack(padx=14, pady=(10,0), anchor="w")

        # result text
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14, pady=12)
        self._label(left, "Hasil :").pack(padx=14, anchor="w")
        self.ks_result = tk.Text(left, font=("Consolas", 10),
                                 bg="#252840", fg=TEXT,
                                 relief="flat", height=7,
                                 state="disabled")
        self.ks_result.pack(padx=14, pady=(4,0), fill="x")

        # canvas
        right = tk.Frame(frame, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        self._label(right, "Visualisasi Barang", 10, True, bg=BG).pack(anchor="w", pady=(0,6))
        self.ks_canvas = tk.Canvas(right, bg=BG, highlightthickness=0)
        self.ks_canvas.pack(fill="both", expand=True)

    def _run_knapsack(self):
        try:
            raw = self.ks_weights.get().replace(" ", "")
            weights = [int(x) for x in raw.split(",") if x]
            target = int(self.ks_target.get())
            if not weights or target < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error",
                "Format: angka dipisah koma, target >= 0")
            return

        self.ks_status.config(text="Mencari solusi...", fg=WARNING)
        self.update()
        t0 = time.time()
        sol = solve_knapsack(sorted(weights), target)
        elapsed = time.time() - t0

        self.ks_result.config(state="normal")
        self.ks_result.delete("1.0", "end")

        if sol:
            self.ks_status.config(
                text=f"✔ Solusi ditemukan  ({elapsed:.4f}s)", fg=SUCCESS)
            chosen_str = " + ".join(str(w) for w in sol)
            self.ks_result.insert("end",
                f"Barang dipilih :\n{sol}\n\n"
                f"Penjumlahan :\n{chosen_str} = {sum(sol)}\n\n"
                f"Target terpenuhi: {sum(sol)} / {target}")
            self._draw_knapsack(sorted(weights), sol, target)
        else:
            self.ks_status.config(text="✘ Tidak ada kombinasi yang sesuai", fg=QUEEN_CLR)
            self.ks_result.insert("end", "Tidak ada solusi ditemukan.")
            self._draw_knapsack(sorted(weights), [], target)
        self.ks_result.config(state="disabled")

    def _draw_knapsack(self, weights, chosen, target):
        c = self.ks_canvas
        c.delete("all")
        c.update()
        W, H = c.winfo_width(), c.winfo_height()

        if not weights:
            return

        n = len(weights)
        bar_w = max(20, min(60, (W - 60) // n - 6))
        gap   = 6
        total_bar_w = n * (bar_w + gap) - gap
        ox = (W - total_bar_w) // 2
        max_w = max(weights)
        max_h = H - 100

        # baseline
        baseline = H - 50
        c.create_line(ox-10, baseline, ox+total_bar_w+10, baseline,
                      fill=BORDER, width=1)

        chosen_set = list(chosen)  # may have duplicates, use counts
        from collections import Counter
        chosen_cnt = Counter(chosen)
        drawn_cnt  = Counter()

        for i, w in enumerate(weights):
            x = ox + i*(bar_w+gap)
            h = int((w / max_w) * max_h * 0.85)
            y = baseline - h

            in_chosen = drawn_cnt[w] < chosen_cnt[w]
            if in_chosen:
                fill = SUCCESS
                drawn_cnt[w] += 1
            else:
                fill = "#334155"

            # bar
            radius = 4
            c.create_rectangle(x, y+radius, x+bar_w, baseline,
                                fill=fill, outline="")
            c.create_rectangle(x, y, x+bar_w, y+radius*2,
                                fill=fill, outline="")
            c.create_oval(x, y, x+radius*2, y+radius*2,
                          fill=fill, outline="")
            c.create_oval(x+bar_w-radius*2, y, x+bar_w, y+radius*2,
                          fill=fill, outline="")

            # weight label on bar
            fs = max(8, int(bar_w * 0.28))
            c.create_text(x+bar_w//2, y-10,
                          text=str(w), fill=TEXT,
                          font=("Consolas", fs, "bold"))
            # bottom index
            c.create_text(x+bar_w//2, baseline+14,
                          text=f"#{i+1}", fill=SUBTEXT,
                          font=("Consolas", 8))

            if in_chosen or drawn_cnt[w] <= chosen_cnt[w]:
                # checkmark
                c.create_text(x+bar_w//2, y+h//2+3,
                              text="✔", fill="white",
                              font=("Arial", max(8, fs)))

        # legend
        c.create_rectangle(ox, H-28, ox+12, H-16, fill=SUCCESS, outline="")
        c.create_text(ox+18, H-22, text="Dipilih", anchor="w",
                      fill=SUCCESS, font=("Consolas", 9))
        c.create_rectangle(ox+80, H-28, ox+92, H-16, fill="#334155", outline="")
        c.create_text(ox+98, H-22, text="Tidak dipilih", anchor="w",
                      fill=SUBTEXT, font=("Consolas", 9))

        # target info
        total = sum(chosen)
        info = f"Total terpilih: {total}  |  Target: {target}"
        c.create_text(W//2, 18, text=info, fill=ACCENT2,
                      font=("Consolas", 10, "bold"))


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()