import tkinter as tk
from collections import deque
import sys

# --- CONFIG MAZE ---
RAW_MAZE = [
    "####################",
    "#S  #     #        #",
    "# ## # ## # ##### ##",
    "# #  #  # #     #  #",
    "# # ## ## ##### # ##",
    "#   #  #     #  #  #",
    "### # ### ## # ### #",
    "#   #   # #  #   # #",
    "# ### # # # ### # ##",
    "# #   # # #   # #  #",
    "# # ### # ### # ## #",
    "#   #   #   # #    #",
    "# ### ####### # ## #",
    "#   #         #  # #",
    "### ########### # ##",
    "#   #       #   #  #",
    "# ### ##### # ###  #",
    "#     #     #   #  #",
    "####### ######### ##",
    "#                 E#",
    "####################",
]

# WARNA TEMA
C_BG      = "#0b1224"
C_WALL    = "#1e3250"
C_OPEN    = "#f0f4fa"
C_START   = "#2ecc71"
C_END     = "#e74c3c"
C_VISITED = "#3498db"
C_PATH    = "#f1c40f"

class MazeGame:
    def __init__(self, algo_choice):
        self.root = tk.Tk()
        self.root.title(f"Maze Solver - Mode: {algo_choice}")
        self.root.configure(bg=C_BG)
        
        self.cell_size = 25
        self.rows = len(RAW_MAZE)
        self.cols = len(RAW_MAZE[0])
        self.algo_choice = algo_choice
        
        self.canvas = tk.Canvas(self.root, width=self.cols*self.cell_size, 
                                height=self.rows*self.cell_size, 
                                bg=C_BG, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        
        self.grid = [list(row) for row in RAW_MAZE]
        self.start_pos = self.find_pos('S')
        self.end_pos = self.find_pos('E')
        
        self.render_all()
        self.root.after(1000, self.start_solving)

    def find_pos(self, char):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == char: return (r, c)
        return None

    def render_all(self, visited=None, path=None):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                color = C_OPEN
                if self.grid[r][c] == '#': color = C_WALL
                elif path and (r, c) in path: color = C_PATH
                elif visited and (r, c) in visited: color = C_VISITED
                
                if (r, c) == self.start_pos: color = C_START
                if (r, c) == self.end_pos: color = C_END
                
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#0b1224")
        self.root.update()

    def start_solving(self):
        if self.algo_choice == "BFS":
            self.solve_logic(is_bfs=True)
        else:
            self.solve_logic(is_bfs=False)

    def solve_logic(self, is_bfs):
        # BFS pakai deque (popleft), DFS pakai list biasa (pop)
        container = deque([self.start_pos])
        visited = {self.start_pos}
        parent = {self.start_pos: None}
        
        while container:
            curr = container.popleft() if is_bfs else container.pop()
            
            if curr != self.start_pos and curr != self.end_pos:
                self.render_all(visited)
            
            if curr == self.end_pos:
                path = []
                while curr:
                    path.append(curr)
                    curr = parent[curr]
                self.render_all(visited, set(path))
                print("\n[HORE] Jalur ditemukan!")
                return

            # Cek tetangga
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = curr[0]+dr, curr[1]+dc
                if 0<=nr<self.rows and 0<=nc<self.cols and \
                   self.grid[nr][nc] != '#' and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    parent[(nr, nc)] = curr
                    container.append((nr, nc))
            
            self.root.after(15) # Delay animasi

def main_terminal():
    print("="*30)
    print("   MAZE SOLVER TERMINAL")
    print("="*30)
    print("Pilih Algoritma:")
    print("1. BFS (Breadth-First Search)")
    print("2. DFS (Depth-First Search)")
    print("3. Keluar")
    
    pilihan = input("\nMasukkan pilihan (1/2/3): ")
    
    if pilihan == '1':
        game = MazeGame("BFS")
        game.root.mainloop()
    elif pilihan == '2':
        game = MazeGame("DFS")
        game.root.mainloop()
    elif pilihan == '3':
        print("Sampai jumpa!")
        sys.exit()
    else:
        print("Pilihan salah! Coba jalankan lagi.")

if __name__ == "__main__":
    main_terminal()