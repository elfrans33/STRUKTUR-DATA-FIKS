from typing import List, Optional
from collections import deque

class ExprHeapSorter:
    def __init__(self, expr_str: str):
        self.expr = expr_str # [cite: 142]
        self.values = [] # [cite: 143]

    def parse_and_evaluate(self) -> List[int]:
        tokens = deque(self.expr) # [cite: 146]
        root = self._build_tree(tokens)
        self.values = self._eval_tree(root)
        return self.values

    def _build_tree(self, tokens: deque) -> Optional[dict]:
        # Implementasi rekursif sesuai instruksi [cite: 151]
        if not tokens: return None
        token = tokens.popleft()

        if token == '(':
            left_node = self._build_tree(tokens)
            op = tokens.popleft() # Ambil operator [cite: 179]
            right_node = self._build_tree(tokens)
            tokens.popleft() # Buang ')' yang menutup [cite: 179]
            return {'val': op, 'left': left_node, 'right': right_node} # [cite: 152]
        else:
            return {'val': token, 'left': None, 'right': None} # Operand [cite: 180]

    def _eval_tree(self, node: Optional[dict]) -> List[int]:
        # Evaluasi postorder [cite: 155]
        if node is None: return []
        
        if node['left'] is None and node['right'] is None:
            return [int(node['val'])]
            
        left_vals = self._eval_tree(node['left'])
        right_vals = self._eval_tree(node['right'])
        
        l_val = left_vals[-1] if left_vals else 0
        r_val = right_vals[-1] if right_vals else 0
        
        op = node['val']
        res = 0
        if op == '+': res = l_val + r_val
        elif op == '-': res = l_val - r_val
        elif op == '*': res = l_val * r_val
        elif op == '/':
            if r_val == 0: raise ValueError("Division by zero") # [cite: 156]
            res = l_val // r_val
            
        return left_vals + right_vals + [res]

    def heapsort_inplace(self, arr: List[int]) -> List[int]:
        n = len(arr) # [cite: 160]
        if n <= 1: return arr
        
        # 1. Build max-heap in-place [cite: 162]
        for i in range(n//2 - 1, -1, -1): # [cite: 163, 184]
            self._sift_down(arr, n, i)
            
        # 2. Extract & sort [cite: 165]
        for end in range(n - 1, 0, -1): # [cite: 166]
            arr[0], arr[end] = arr[end], arr[0] # Swap [cite: 167]
            self._sift_down(arr, end, 0) # [cite: 168]
            
        return arr

    def _sift_down(self, arr: List[int], heap_size: int, idx: int):
        largest = idx
        left = 2 * idx + 1 # [cite: 172]
        right = 2 * idx + 2 # [cite: 172]

        if left < heap_size and arr[left] > arr[largest]:
            largest = left
        if right < heap_size and arr[right] > arr[largest]:
            largest = right

        if largest != idx:
            arr[idx], arr[largest] = arr[largest], arr[idx] # Swap [cite: 181]
            self._sift_down(arr, heap_size, largest)

    def is_complete_tree(self, arr: List[int]) -> bool:
        n = len(arr)
        # Memvalidasi properti complete binary tree [cite: 175, 176]
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            # Jika ada anak kiri di luar bounds tapi ada elemen sisa, atau lompat [cite: 182, 183]
            if left >= n and right < n:
                return False
        return True
    
    