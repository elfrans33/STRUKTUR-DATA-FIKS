import time
import random

def countInversionsNaive(arr):
    count = 0
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                count += 1
    return count

def countInversionsSmart(arr):
    if len(arr) <= 1:
        return arr, 0
    
    mid = len(arr) // 2
    left, left_inv = countInversionsSmart(arr[:mid])
    right, right_inv = countInversionsSmart(arr[mid:])
    merged, split_inv = merge_and_count(left, right)
    
    return merged, left_inv + right_inv + split_inv

def merge_and_count(left, right):
    result = []
    i = j = inv_count = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            # Jika elemen di kanan lebih kecil, terjadi inversi dengan SEMUA sisa elemen di kiri
            result.append(right[j])
            inv_count += (len(left) - i)
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result, inv_count

# Pengujian Kecepatan
for n in [1000, 5000, 10000]:
    test_arr = [random.randint(0, 10000) for _ in range(n)]
    
    start = time.time()
    naive_res = countInversionsNaive(test_arr)
    t_naive = time.time() - start
    
    start = time.time()
    _, smart_res = countInversionsSmart(test_arr)
    t_smart = time.time() - start
    
    print(f"N={n} | Naive: {t_naive:.4f}s (Res: {naive_res}) | Smart: {t_smart:.4f}s (Res: {smart_res})")