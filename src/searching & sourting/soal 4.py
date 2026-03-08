def mergeThreeSortedLists(listA, listB, listC):
    result = []
    i = j = k = 0
    
    # Ambil nilai infinity untuk memudahkan perbandingan jika salah satu list habis
    inf = float('inf')
    
    total_elements = len(listA) + len(listB) + len(listC)
    
    while len(result) < total_elements:
        valA = listA[i] if i < len(listA) else inf
        valB = listB[j] if j < len(listB) else inf
        valC = listC[k] if k < len(listC) else inf
        
        # Cari yang terkecil dari ketiga pointer
        if valA <= valB and valA <= valC:
            result.append(valA)
            i += 1
        elif valB <= valA and valB <= valC:
            result.append(valB)
            j += 1
        else:
            result.append(valC)
            k += 1
            
    return result

# Uji Coba
print(mergeThreeSortedLists([1, 5, 9], [2, 6, 10], [3, 4, 7]))