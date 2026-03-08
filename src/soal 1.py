def find_bound(arr, target, find_first):
    low, high = 0, len(arr) - 1
    result = -1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            result = mid
            if find_first:
                high = mid - 1 # Terus cari ke kiri
            else:
                low = mid + 1  # Terus cari ke kanan
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return result

def countOccurrences(sortedList, target):
    first = find_bound(sortedList, target, True)
    if first == -1:
        return 0
    last = find_bound(sortedList, target, False)
    return last - first + 1

# Uji Coba
print(f"Hasil 1: {countOccurrences([1, 2, 4, 4, 4, 4, 7, 9, 12], 4)}") # Output: 4
print(f"Hasil 2: {countOccurrences([1, 2, 4, 4, 4, 4, 7, 9, 12], 5)}") # Output: 0