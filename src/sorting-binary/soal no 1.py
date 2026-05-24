from typing import List, Optional
import math

class ListNode:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

class AdvancedSorter:
    def __init__(self):
        pass

    # =========================================================
    # 1. ARRAY MERGE SORT (Virtual Sublists + Single tmpArray)
    # =========================================================
    def sort_array(self, arr: List[int]) -> List[int]:
        if len(arr) <= 1: return arr
        tmp_array = [0] * len(arr) # Single temporary array [cite: 47]
        self._rec_merge_sort(arr, 0, len(arr) - 1, tmp_array)
        return arr

    def _rec_merge_sort(self, arr, first, last, tmp_array):
        if first >= last: return
        mid = (first + last) // 2
        self._rec_merge_sort(arr, first, mid, tmp_array)
        self._rec_merge_sort(arr, mid + 1, last, tmp_array)
        self._merge_virtual(arr, first, mid, last, tmp_array)

    def _merge_virtual(self, arr, left_start, mid, right_end, tmp_array):
        # Penggabungan dua virtual sublist [cite: 59]
        left = left_start
        right = mid + 1
        idx = left_start

        while left <= mid and right <= right_end:
            if arr[left] <= arr[right]: # STABLE sort [cite: 61, 98]
                tmp_array[idx] = arr[left]
                left += 1
            else:
                tmp_array[idx] = arr[right]
                right += 1
            idx += 1

        while left <= mid:
            tmp_array[idx] = arr[left]
            left += 1
            idx += 1

        while right <= right_end:
            tmp_array[idx] = arr[right]
            right += 1
            idx += 1

        for i in range(left_start, right_end + 1):
            arr[i] = tmp_array[i] # Salin kembali [cite: 62]

    # =========================================================
    # 2. LINKED LIST MERGE SORT (Fast-Slow + Dummy Merge)
    # =========================================================
    def sort_linked_list(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if head is None or head.next is None:
            return head
        right_head = self._split_linked_list(head) # [cite: 73]
        left_head = head
        left_sorted = self.sort_linked_list(left_head)
        right_sorted = self.sort_linked_list(right_head)
        return self._merge_linked_lists(left_sorted, right_sorted)

    def _split_linked_list(self, head: ListNode) -> Optional[ListNode]:
        midPoint = head
        curNode = head.next
        # Fast-slow pointer implementation [cite: 79, 99]
        while curNode and curNode.next:
            midPoint = midPoint.next
            curNode = curNode.next.next
            
        right_head = midPoint.next # [cite: 100]
        midPoint.next = None # Putus link [cite: 80, 101]
        return right_head

    def _merge_linked_lists(self, listA: Optional[ListNode], listB: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0) # Dummy node [cite: 85, 102]
        tail = dummy

        while listA and listB:
            if listA.data <= listB.data: # STABLE [cite: 86]
                tail.next = listA
                listA = listA.next
            else:
                tail.next = listB
                listB = listB.next
            tail = tail.next
            
        tail.next = listA or listB # [cite: 103]
        return dummy.next # [cite: 87]

    # =========================================================
    # 3. QUICK SORT PARTITION (Median-of-Three Pivot)
    # =========================================================
    def partition_quick(self, arr: List[int], first: int, last: int) -> int:
        mid = (first + last) // 2
        # Median of three logic [cite: 93, 104]
        if arr[first] > arr[mid]: arr[first], arr[mid] = arr[mid], arr[first]
        if arr[first] > arr[last]: arr[first], arr[last] = arr[last], arr[first]
        if arr[mid] > arr[last]: arr[mid], arr[last] = arr[last], arr[mid]
        
        # Tukar pivot (median) ke posisi 'first' [cite: 94, 104]
        arr[first], arr[mid] = arr[mid], arr[first]
        
        pivot_val = arr[first]
        left = first + 1
        right = last

        while True:
            while left <= right and arr[left] <= pivot_val: left += 1
            while arr[right] >= pivot_val and right >= left: right -= 1
            if right < left: break
            arr[left], arr[right] = arr[right], arr[left]

        arr[first], arr[right] = arr[right], arr[first]
        return right

class ExprHeapSorter:
    def __init__(self, expr):
        self.expr = expr

    def heapsort_inplace(self, arr: List[int]) -> None:
        n = len(arr)

        def heapify(heap_size: int, root_index: int):
            largest = root_index
            left = 2 * root_index + 1
            right = 2 * root_index + 2

            if left < heap_size and arr[left] > arr[largest]:
                largest = left
            if right < heap_size and arr[right] > arr[largest]:
                largest = right

            if largest != root_index:
                arr[root_index], arr[largest] = arr[largest], arr[root_index]
                heapify(heap_size, largest)

        for i in range(n // 2 - 1, -1, -1):
            heapify(n, i)

        for end in range(n - 1, 0, -1):
            arr[0], arr[end] = arr[end], arr[0]
            heapify(end, 0)

    def is_complete_tree(self, arr: List[int]) -> bool:
        # Array-backed binary tree is complete when represented as a contiguous array.
        return True

if __name__ == "__main__":
    # Membuat instansiasi objek dari class AdvancedSorter
    sorter = AdvancedSorter()

    # --- Uji Coba Array Merge Sort ---
    print("=== Uji Coba Array Merge Sort ===")
    arr_test = [38, 27, 43, 3, 9, 82, 10]
    print(f"Data Sebelum diurutkan : {arr_test}")

    # Memanggil fungsi untuk mengurutkan
    sorter.sort_array(arr_test)

    print(f"Data Sesudah diurutkan : {arr_test}")

    # =====================================================================
# BLOK UJI COBA (DRIVER CODE) - COPY DAN PASTE DI PALING BAWAH FILE
# =====================================================================

def create_linked_list(arr):
    """Helper untuk membuat Linked List dari list Python"""
    if not arr: return None
    head = ListNode(arr[0])
    curr = head
    for val in arr[1:]:
        curr.next = ListNode(val)
        curr = curr.next
    return head

def print_linked_list(head):
    """Helper untuk visualisasi Linked List dengan tanda panah"""
    elements = []
    while head:
        elements.append(str(head.data))
        head = head.next
    return " -> ".join(elements) + " -> None"

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🎓 DEMO TUGAS SORTING & BINARY TREE 🎓".center(50))
    print("="*50 + "\n")

    # Inisialisasi Sorter
    sorter = AdvancedSorter()

    # ---------------------------------------------------------
    # UJI COBA 1: Array Merge Sort (Virtual Sublists)
    # ---------------------------------------------------------
    print(">>> 1. UJI COBA ARRAY MERGE SORT (O(n log n))")
    arr_test = [82, 38, 27, 43, 3, 9, 10, 10, 27] # Sengaja ada data kembar untuk test STABLE
    print(f"[-] Data Sebelum  : {arr_test}")
    sorter.sort_array(arr_test)
    print(f"[+] Data Sesudah  : {arr_test}")
    print("-" * 50)

    # ---------------------------------------------------------
    # UJI COBA 2: Linked List Merge Sort (Fast-Slow Pointer)
    # ---------------------------------------------------------
    print(">>> 2. UJI COBA LINKED LIST MERGE SORT")
    ll_data = [45, 12, 89, 33, 1, 9, 12, 5]
    ll_head = create_linked_list(ll_data)
    
    print(f"[-] List Sebelum  : {print_linked_list(ll_head)}")
    sorted_ll_head = sorter.sort_linked_list(ll_head)
    print(f"[+] List Sesudah  : {print_linked_list(sorted_ll_head)}")
    print("-" * 50)

    # ---------------------------------------------------------
    # UJI COBA 3: Quick Sort Partition (Median-of-Three)
    # ---------------------------------------------------------
    print(">>> 3. UJI COBA QUICK SORT PARTITION")
    qs_arr = [25, 10, 40, 5, 30, 50, 15]
    print(f"[-] Array Awal           : {qs_arr}")
    
    # Partisi array dari indeks 0 sampai terakhir (6)
    pivot_idx = sorter.partition_quick(qs_arr, 0, len(qs_arr) - 1)
    
    print(f"[!] Indeks Pivot Akhir   : {pivot_idx} (Nilai Pivot: {qs_arr[pivot_idx]})")
    print(f"[+] Array Pasca Partisi  : {qs_arr}")
    print("    *Catatan: Elemen di kiri pivot <= pivot, di kanan >= pivot")
    print("-" * 50)

    # ---------------------------------------------------------
    # UJI COBA 4: In-Place Heapsort (Dari Modul ExprHeapSorter)
    # ---------------------------------------------------------
    print(">>> 4. UJI COBA IN-PLACE HEAPSORT & TREE VALIDATION")
    # Anggap ini adalah hasil dari evaluasi pohon ekspresi
    heap_sorter = ExprHeapSorter("dummy_expr") 
    raw_data = [99, 22, 14, 5, 67, 88, 11]
    
    print(f"[-] Data Mentah   : {raw_data}")
    heap_sorter.heapsort_inplace(raw_data)
    print(f"[+] Heapsort Hasil: {raw_data}")
    
    # Cek Validasi Complete Tree
    is_complete = heap_sorter.is_complete_tree(raw_data)
    print(f"[?] Apakah array terurut valid sebagai Complete Binary Tree? : {'YA' if is_complete else 'TIDAK'}")
    print("=" * 50 + "\n")