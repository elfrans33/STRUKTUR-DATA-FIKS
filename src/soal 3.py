import random

def insertion_sort(arr):
    ops = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            ops += 1 # Comparison
            if arr[j] > key:
                arr[j+1] = arr[j]
                ops += 1 # Swap-like move
                j -= 1
            else:
                break
        arr[j+1] = key
    return ops

def selection_sort(arr):
    ops = 0
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            ops += 1 # Comparison
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        ops += 1 # Swap
    return ops

def hybridSort(theSeq, threshold=10):
    if len(theSeq) <= threshold:
        return insertion_sort(theSeq)
    else:
        return selection_sort(theSeq)

# Eksperimen
sizes = [50, 100, 500]
print(f"{'Size':<10} | {'Hybrid':<10} | {'Pure Ins':<10} | {'Pure Sel':<10}")
print("-" * 50)
for s in sizes:
    data = [random.randint(0, 1000) for _ in range(s)]
    h_ops = hybridSort(data.copy())
    i_ops = insertion_sort(data.copy())
    s_ops = selection_sort(data.copy())
    print(f"{s:<10} | {h_ops:<10} | {i_ops:<10} | {s_ops:<10}")