import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# =========================================================
# GENERATOR FUNGSI HEAPSORT (Untuk menghasilkan frame animasi)
# =========================================================
def sift_down_generator(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i] # Swap
        yield arr # Kirim state (kondisi) array saat ini ke pembuat animasi
        yield from sift_down_generator(arr, n, largest)

def heapsort_generator(arr):
    n = len(arr)
    # 1. Build Max-Heap
    for i in range(n // 2 - 1, -1, -1):
        yield from sift_down_generator(arr, n, i)

    # 2. Extract elements & sort
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0] # Swap root ke belakang
        yield arr # Kirim state
        yield from sift_down_generator(arr, i, 0)

# =========================================================
# SETTING VISUALISASI MATPLOTLIB
# =========================================================
if __name__ == "__main__":
    # Buat 40 data acak dari angka 1 sampai 100
    N = 40
    arr = [random.randint(1, 100) for _ in range(N)]

    # Siapkan figure/jendela animasi
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Animasi In-Place Heapsort (Tugas Algoritma)", fontsize=16, pad=20)
    ax.set_xlabel("Indeks Array", fontsize=12)
    ax.set_ylabel("Nilai Data", fontsize=12)
    
    # Buat diagram batang (bar chart) awal
    bar_rects = ax.bar(range(len(arr)), arr, align="edge", color="skyblue", edgecolor="black")
    ax.set_xlim(0, N)
    ax.set_ylim(0, int(1.1 * max(arr)))

    # Teks indikator jumlah operasi (swaps/perbandingan)
    text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=12, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    iteration = [0] # Gunakan list agar bisa diubah di dalam fungsi nested

    def update_fig(arr_state, rects, iteration):
        # Fungsi ini dipanggil berulang kali untuk memperbarui gambar balok
        for rect, val in zip(rects, arr_state):
            rect.set_height(val)
            # Warnai hijau jika sudah di area yang terurut (di bagian kanan), sisanya biru
            # (Untuk Heapsort, ini agak dinamis, kita pakai warna biru/merah saja biar keren)
            rect.set_color("royalblue") 
            rect.set_edgecolor("black")
        
        iteration[0] += 1
        text.set_text(f"Langkah Operasi: {iteration[0]}")
        return rects

    # Masukkan generator heapsort ke FuncAnimation
    generator = heapsort_generator(arr)
    
    anim = animation.FuncAnimation(
        fig, 
        func=update_fig,
        fargs=(bar_rects, iteration), 
        frames=generator, 
        interval=100,      # Kecepatan animasi (milidetik). Ubah ke 50 jika ingin lebih cepat!
        repeat=False,      # Berhenti ketika sudah selesai
        save_count=1000    # Cegah warning batas frame
    )

    # Tampilkan jendela animasinya!
    plt.show()

    