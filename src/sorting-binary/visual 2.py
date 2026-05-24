
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# =========================================================
# 1. DATA SEJARAH KURS USD KE IDR (Data Milestone Representatif)
# Sumber: Arsip Sejarah Bank Indonesia & Data Makroekonomi
# =========================================================
historical_data = [
    {"year": 1949, "rate": 3.8},       
    {"year": 1965, "rate": 10000},     
    {"year": 1971, "rate": 415},       
    {"year": 1980, "rate": 625},       
    {"year": 1990, "rate": 1901},      
    {"year": 1997, "rate": 4650},      
    {"year": 1998, "rate": 16650},     
    {"year": 2001, "rate": 10260},     
    {"year": 2008, "rate": 10950},     
    {"year": 2014, "rate": 12440},     
    {"year": 2020, "rate": 14500},     
    {"year": 2024, "rate": 15800},     
    {"year": 2026, "rate": 16200}      
]

years = [d["year"] for d in historical_data]
rates = [d["rate"] for d in historical_data]

# =========================================================
# 2. ALGORITMA SORTING (Heapsort In-Place)
# =========================================================
def sift_down(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left]["rate"] > arr[largest]["rate"]:
        largest = left
    if right < n and arr[right]["rate"] > arr[largest]["rate"]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        sift_down(arr, n, largest)

def heapsort_historical(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        sift_down(arr, i, 0)
    return arr

sorted_data = heapsort_historical(historical_data.copy())

# =========================================================
# 3. VISUALISASI DENGAN MATPLOTLIB (Versi Dirapikan)
# =========================================================
# Memperlebar ukuran figure agar tidak berdesakan
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Analisis Sejarah Nilai Tukar USD ke IDR (1949 - 2026)", fontsize=18, fontweight='bold', y=0.98)

# --- GRAFIK 1: TIME SERIES ---
ax1.plot(years, rates, marker='o', linestyle='-', color='#B22222', linewidth=2.5, markersize=8)
ax1.fill_between(years, rates, color='#B22222', alpha=0.15)
ax1.set_title("Grafik Fluktuasi Kurs (Berdasarkan Tahun)", fontsize=14, pad=15)
ax1.set_xlabel("Tahun", fontsize=12, fontweight='bold')
ax1.set_ylabel("Nilai Tukar (Rp / 1 USD)", fontsize=12, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.7)

# Format Sumbu Y agar ada titik pemisah ribuan (contoh: 15.000)
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', '.')))

# Penyesuaian posisi teks anotasi agar lebih terbaca
ax1.annotate('Krisis Moneter\n(1998)', xy=(1998, 16650), xytext=(1975, 15000),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
             fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

ax1.annotate('Hiperinflasi\n(1965)', xy=(1965, 10000), xytext=(1945, 12000),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
             fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

# --- GRAFIK 2: BAR CHART (Hasil Sorting) ---
top_5_weakest = sorted_data[-5:]
top_5_weakest.reverse() 

labels = [str(d["year"]) for d in top_5_weakest]
values = [d["rate"] for d in top_5_weakest]
colors = ['#8B0000', '#A52A2A', '#B22222', '#CD5C5C', '#F08080']

bars = ax2.bar(labels, values, color=colors, edgecolor='black', width=0.7)
ax2.set_title("5 Tahun dengan Nilai Rupiah Terlemah", fontsize=14, pad=15)
ax2.set_xlabel("Tahun Kejadian", fontsize=12, fontweight='bold')
ax2.set_ylabel("Nilai Tukar (Rp)", fontsize=12, fontweight='bold')

# Format Sumbu Y untuk bar chart
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',').replace(',', '.')))
ax2.grid(axis='y', linestyle='--', alpha=0.5)

# Label angka di atas balok dengan pemisah ribuan
for bar in bars:
    yval = bar.get_height()
    formatted_val = f"Rp {int(yval):,}".replace(',', '.')
    ax2.text(bar.get_x() + bar.get_width()/2, yval + 150, formatted_val, 
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# --- FOOTNOTE (Catatan Kaki untuk Disclaimer) ---
fig.text(0.01, 0.02, 
         "*Catatan: Angka 1965 merepresentasikan kondisi sebelum 'Sanering' (pemotongan nilai uang) oleh pemerintah pada akhir tahun tersebut.\n"
         "Sumber Referensi: Arsip Historis Bank Indonesia & Data Makroekonomi Global.", 
         fontsize=9, style='italic', color='gray')

# Merapikan jarak antar elemen
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.show()