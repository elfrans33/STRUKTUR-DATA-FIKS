# ============================================================
# Struktur Data Aplikasi Note-Taking
# Slide 39 - Chapter 9 Advanced Linked Lists
# ============================================================
# Fitur:
#   1. Multiple tags per note (multi-linked by tag)
#   2. Chronological & alphabetical views (doubly linked sorted)
#   3. Sync status tracking (circular buffer for recent changes)
# ============================================================

import uuid
from datetime import datetime


# ============================================================
# 1. NOTE NODE — inti data, punya 4 pointer untuk 2 DLL chain
# ============================================================

class NoteNode:
    def __init__(self, title: str, content: str):
        self.id         = str(uuid.uuid4())[:8]   # ID pendek untuk demo
        self.title      = title
        self.content    = content
        self.created_at = datetime.now()
        self.tags       = []                       # list nama tag

        # Chain 1: Doubly Linked List by date (chronological)
        self.chrono_prev = None
        self.chrono_next = None

        # Chain 2: Doubly Linked List by title (alphabetical)
        self.alpha_prev  = None
        self.alpha_next  = None

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def __repr__(self):
        return f"Note({self.id!r}, title={self.title!r}, tags={self.tags})"


# ============================================================
# 2. TAG MAP — hash map: tag_name → list of NoteNode
# ============================================================

class TagMap:
    def __init__(self):
        self._map: dict[str, list[NoteNode]] = {}

    def add(self, tag: str, note: NoteNode):
        if tag not in self._map:
            self._map[tag] = []
        if note not in self._map[tag]:
            self._map[tag].append(note)

    def remove(self, tag: str, note: NoteNode):
        if tag in self._map:
            self._map[tag] = [n for n in self._map[tag] if n is not note]
            if not self._map[tag]:
                del self._map[tag]

    def get_notes_by_tag(self, tag: str) -> list[NoteNode]:
        return self._map.get(tag, [])

    def all_tags(self) -> list[str]:
        return list(self._map.keys())

    def __repr__(self):
        return f"TagMap({{{', '.join(f'{k!r}: {len(v)} note(s)' for k,v in self._map.items())}}})"


# ============================================================
# 3. SYNC CHANGE — isi tiap slot circular buffer
# ============================================================

class SyncChange:
    PENDING = "pending"
    SYNCED  = "synced"
    FAILED  = "failed"

    def __init__(self, note_id: str, operation: str, snapshot: dict):
        self.note_id   = note_id
        self.operation = operation          # 'ADD' | 'EDIT' | 'DEL'
        self.timestamp = datetime.now()
        self.status    = SyncChange.PENDING
        self.snapshot  = snapshot           # salinan data saat perubahan

    def mark_synced(self):
        self.status = SyncChange.SYNCED

    def mark_failed(self):
        self.status = SyncChange.FAILED

    def __repr__(self):
        ts = self.timestamp.strftime("%H:%M:%S")
        return (f"SyncChange(id={self.note_id!r}, op={self.operation!r}, "
                f"status={self.status!r}, time={ts})")


# ============================================================
# 4. CIRCULAR BUFFER — tracking perubahan terbaru
# ============================================================

class CircularBuffer:
    def __init__(self, capacity: int = 5):
        self._capacity = capacity
        self._buffer   = [None] * capacity   # array tetap
        self._head     = 0                   # index tertua
        self._tail     = 0                   # index untuk write berikutnya
        self._size     = 0                   # jumlah elemen aktif

    def push(self, change: SyncChange):
        """Tambah perubahan baru. Kalau penuh, timpa yang paling lama."""
        self._buffer[self._tail] = change
        if self._size == self._capacity:
            # Buffer penuh → head maju (oldest overwritten)
            self._head = (self._head + 1) % self._capacity
        else:
            self._size += 1
        self._tail = (self._tail + 1) % self._capacity

    def get_recent(self, n: int = None) -> list[SyncChange]:
        """Ambil n perubahan terbaru (default: semua)."""
        if n is None:
            n = self._size
        n = min(n, self._size)
        result = []
        for i in range(n):
            idx = (self._tail - 1 - i) % self._capacity
            result.append(self._buffer[idx])
        return result

    def get_pending(self) -> list[SyncChange]:
        """Ambil semua perubahan yang belum ter-sync."""
        return [c for c in self.get_recent() if c.status == SyncChange.PENDING]

    def __len__(self):
        return self._size

    def __repr__(self):
        items = self.get_recent()
        return f"CircularBuffer(size={self._size}/{self._capacity}, items={items})"


# ============================================================
# 5. NOTE APP — kelas utama yang menyatukan semua komponen
# ============================================================

class NoteApp:
    def __init__(self, buffer_capacity: int = 5):
        # Doubly Linked List — chain chronological
        self._chrono_head: NoteNode = None
        self._chrono_tail: NoteNode = None

        # Doubly Linked List — chain alphabetical
        self._alpha_head:  NoteNode = None
        self._alpha_tail:  NoteNode = None

        # Tag map
        self._tag_map = TagMap()

        # Circular buffer untuk sync tracking
        self._sync_buffer = CircularBuffer(buffer_capacity)

    # ── Helper: insert ke chain chronological (sorted by created_at) ────
    def _chrono_insert(self, note: NoteNode):
        if self._chrono_head is None:
            self._chrono_head = note
            self._chrono_tail = note
            return
        # Insert di akhir (karena note baru selalu paling baru)
        note.chrono_prev = self._chrono_tail
        self._chrono_tail.chrono_next = note
        self._chrono_tail = note

    # ── Helper: insert ke chain alphabetical (sorted by title A-Z) ──────
    def _alpha_insert(self, note: NoteNode):
        if self._alpha_head is None:
            self._alpha_head = note
            self._alpha_tail = note
            return
        # Cari posisi yang tepat
        cur = self._alpha_head
        while cur is not None and cur.title.lower() < note.title.lower():
            cur = cur.alpha_next

        if cur is None:
            # Insert di akhir
            note.alpha_prev = self._alpha_tail
            self._alpha_tail.alpha_next = note
            self._alpha_tail = note
        elif cur is self._alpha_head:
            # Insert di depan
            note.alpha_next = self._alpha_head
            self._alpha_head.alpha_prev = note
            self._alpha_head = note
        else:
            # Insert di tengah
            note.alpha_next = cur
            note.alpha_prev = cur.alpha_prev
            cur.alpha_prev.alpha_next = note
            cur.alpha_prev = note

    # ── Helper: hapus dari chain chronological ──────────────────────────
    def _chrono_remove(self, note: NoteNode):
        if note.chrono_prev:
            note.chrono_prev.chrono_next = note.chrono_next
        else:
            self._chrono_head = note.chrono_next
        if note.chrono_next:
            note.chrono_next.chrono_prev = note.chrono_prev
        else:
            self._chrono_tail = note.chrono_prev
        note.chrono_prev = note.chrono_next = None

    # ── Helper: hapus dari chain alphabetical ───────────────────────────
    def _alpha_remove(self, note: NoteNode):
        if note.alpha_prev:
            note.alpha_prev.alpha_next = note.alpha_next
        else:
            self._alpha_head = note.alpha_next
        if note.alpha_next:
            note.alpha_next.alpha_prev = note.alpha_prev
        else:
            self._alpha_tail = note.alpha_prev
        note.alpha_prev = note.alpha_next = None

    # ── PUBLIC: Tambah note baru ────────────────────────────────────────
    def add_note(self, title: str, content: str, tags: list[str] = None) -> NoteNode:
        note = NoteNode(title, content)

        # Masukkan ke kedua chain DLL
        self._chrono_insert(note)
        self._alpha_insert(note)

        # Daftarkan tags ke TagMap
        for tag in (tags or []):
            note.add_tag(tag)
            self._tag_map.add(tag, note)

        # Catat ke circular buffer
        self._sync_buffer.push(SyncChange(
            note_id=note.id,
            operation='ADD',
            snapshot={'title': title, 'content': content, 'tags': tags or []}
        ))
        return note

    # ── PUBLIC: Edit note ───────────────────────────────────────────────
    def edit_note(self, note: NoteNode, title: str = None, content: str = None,
                  add_tags: list[str] = None, remove_tags: list[str] = None):
        old_title = note.title

        if title and title != note.title:
            # Judul berubah → posisi alphabetical berubah, perlu re-insert
            self._alpha_remove(note)
            note.title = title
            self._alpha_insert(note)

        if content:
            note.content = content

        for tag in (add_tags or []):
            note.add_tag(tag)
            self._tag_map.add(tag, note)

        for tag in (remove_tags or []):
            if tag in note.tags:
                note.tags.remove(tag)
            self._tag_map.remove(tag, note)

        # Catat ke circular buffer
        self._sync_buffer.push(SyncChange(
            note_id=note.id,
            operation='EDIT',
            snapshot={'title': note.title, 'content': note.content, 'tags': note.tags[:]}
        ))

    # ── PUBLIC: Hapus note ──────────────────────────────────────────────
    def delete_note(self, note: NoteNode):
        self._chrono_remove(note)
        self._alpha_remove(note)

        for tag in note.tags:
            self._tag_map.remove(tag, note)

        self._sync_buffer.push(SyncChange(
            note_id=note.id,
            operation='DEL',
            snapshot={'title': note.title}
        ))

    # ── PUBLIC: Tampilkan semua note urutan tanggal ─────────────────────
    def view_chronological(self) -> list[NoteNode]:
        result = []
        cur = self._chrono_head
        while cur is not None:
            result.append(cur)
            cur = cur.chrono_next
        return result

    # ── PUBLIC: Tampilkan semua note urutan abjad ───────────────────────
    def view_alphabetical(self) -> list[NoteNode]:
        result = []
        cur = self._alpha_head
        while cur is not None:
            result.append(cur)
            cur = cur.alpha_next
        return result

    # ── PUBLIC: Cari note berdasarkan tag ──────────────────────────────
    def find_by_tag(self, tag: str) -> list[NoteNode]:
        return self._tag_map.get_notes_by_tag(tag)

    # ── PUBLIC: Lihat status sync buffer ───────────────────────────────
    def sync_status(self) -> list[SyncChange]:
        return self._sync_buffer.get_recent()

    def pending_sync(self) -> list[SyncChange]:
        return self._sync_buffer.get_pending()


# ============================================================
# DEMO — uji semua fitur
# ============================================================

def demo():
    print("=" * 60)
    print("  DEMO NOTE-TAKING APP — Advanced Linked Lists")
    print("=" * 60)

    app = NoteApp(buffer_capacity=5)

    # --- Tambah beberapa note ---
    print("\n[1] MENAMBAH NOTE")
    n1 = app.add_note("Python Basics",    "Belajar variabel, loop, fungsi",   tags=["python", "belajar"])
    n2 = app.add_note("Algoritma Sorting","Bubble, merge, quick sort",         tags=["algoritma", "belajar"])
    n3 = app.add_note("Database SQL",     "SELECT, JOIN, index",               tags=["database", "sql"])
    n4 = app.add_note("Linked List",      "Singly, doubly, circular",          tags=["python", "algoritma"])
    n5 = app.add_note("Docker Intro",     "Container, image, compose",         tags=["devops"])

    for n in [n1,n2,n3,n4,n5]:
        print(f"  + {n}")

    # --- View chronological ---
    print("\n[2] VIEW CHRONOLOGICAL (urutan dibuat)")
    for i, n in enumerate(app.view_chronological(), 1):
        print(f"  {i}. [{n.id}] {n.title}  tags={n.tags}")

    # --- View alphabetical ---
    print("\n[3] VIEW ALPHABETICAL (urutan judul A-Z)")
    for i, n in enumerate(app.view_alphabetical(), 1):
        print(f"  {i}. [{n.id}] {n.title}  tags={n.tags}")

    # --- Cari by tag ---
    print("\n[4] CARI NOTES DENGAN TAG 'python'")
    for n in app.find_by_tag("python"):
        print(f"  - {n.title}")

    print("\n[5] CARI NOTES DENGAN TAG 'belajar'")
    for n in app.find_by_tag("belajar"):
        print(f"  - {n.title}")

    # --- Edit note ---
    print("\n[6] EDIT NOTE: ubah judul 'Python Basics' → 'Advanced Python'")
    app.edit_note(n1, title="Advanced Python", add_tags=["advanced"])
    print("  Alphabetical setelah edit:")
    for i, n in enumerate(app.view_alphabetical(), 1):
        print(f"  {i}. {n.title}")

    # --- Delete note ---
    print("\n[7] DELETE NOTE: hapus 'Docker Intro'")
    app.delete_note(n5)
    print("  Chronological setelah delete:")
    for i, n in enumerate(app.view_chronological(), 1):
        print(f"  {i}. {n.title}")

    # --- Circular buffer status ---
    print("\n[8] SYNC BUFFER STATUS (5 perubahan terbaru)")
    for c in app.sync_status():
        print(f"  {c}")

    print("\n[9] PENDING SYNC (belum ter-sync)")
    pending = app.pending_sync()
    if pending:
        for c in pending:
            print(f"  {c}")
    else:
        print("  (semua sudah sync)")

    # --- Simulasi sync ---
    print("\n[10] SIMULASI: mark 3 perubahan pertama sebagai 'synced'")
    changes = app.sync_status()
    for c in changes[-3:]:      # 3 yang paling lama
        c.mark_synced()
    print("  Pending setelah sync:")
    pending = app.pending_sync()
    for c in pending:
        print(f"  {c}")

    # --- Overflow buffer ---
    print("\n[11] OVERFLOW BUFFER — tambah 3 note lagi (buffer kapasitas 5)")
    nx1 = app.add_note("Redis Cache",  "Key-value store", tags=["database"])
    nx2 = app.add_note("Git Flow",     "Branch strategy", tags=["devops"])
    nx3 = app.add_note("REST API",     "HTTP methods",    tags=["backend"])
    print(f"  Buffer sekarang berisi {len(app._sync_buffer)} perubahan:")
    for c in app.sync_status():
        print(f"  {c}")
    print("  (Perubahan paling lama otomatis tertimpa karena buffer penuh)")

    print("\n" + "=" * 60)
    print("  SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    demo()
    # ============================================================
# Struktur Data Aplikasi Note-Taking — dengan Visualisasi
# Slide 39 - Chapter 9 Advanced Linked Lists
# ============================================================

import uuid
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from datetime import datetime

# Simpan gambar di folder yang sama dengan file .py ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# 1. NOTE NODE
# ============================================================

class NoteNode:
    def __init__(self, title: str, content: str):
        self.id          = str(uuid.uuid4())[:6]
        self.title       = title
        self.content     = content
        self.created_at  = datetime.now()
        self.tags        = []
        self.chrono_prev = None
        self.chrono_next = None
        self.alpha_prev  = None
        self.alpha_next  = None

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def __repr__(self):
        return f"Note({self.id!r}, {self.title!r}, tags={self.tags})"


# ============================================================
# 2. TAG MAP
# ============================================================

class TagMap:
    def __init__(self):
        self._map: dict[str, list[NoteNode]] = {}

    def add(self, tag: str, note: NoteNode):
        if tag not in self._map:
            self._map[tag] = []
        if note not in self._map[tag]:
            self._map[tag].append(note)

    def remove(self, tag: str, note: NoteNode):
        if tag in self._map:
            self._map[tag] = [n for n in self._map[tag] if n is not note]
            if not self._map[tag]:
                del self._map[tag]

    def get_notes_by_tag(self, tag: str) -> list:
        return self._map.get(tag, [])

    def all_tags(self) -> list:
        return list(self._map.keys())


# ============================================================
# 3. SYNC CHANGE
# ============================================================

class SyncChange:
    PENDING = "pending"
    SYNCED  = "synced"
    FAILED  = "failed"

    def __init__(self, note_id: str, operation: str, snapshot: dict):
        self.note_id   = note_id
        self.operation = operation
        self.timestamp = datetime.now()
        self.status    = SyncChange.PENDING
        self.snapshot  = snapshot

    def mark_synced(self):
        self.status = SyncChange.SYNCED

    def mark_failed(self):
        self.status = SyncChange.FAILED

    def __repr__(self):
        ts = self.timestamp.strftime("%H:%M:%S")
        return f"SyncChange({self.note_id!r}, {self.operation!r}, {self.status!r}, {ts})"


# ============================================================
# 4. CIRCULAR BUFFER
# ============================================================

class CircularBuffer:
    def __init__(self, capacity: int = 5):
        self._capacity = capacity
        self._buffer   = [None] * capacity
        self._head     = 0
        self._tail     = 0
        self._size     = 0

    def push(self, change: SyncChange):
        self._buffer[self._tail] = change
        if self._size == self._capacity:
            self._head = (self._head + 1) % self._capacity
        else:
            self._size += 1
        self._tail = (self._tail + 1) % self._capacity

    def get_recent(self, n: int = None) -> list:
        if n is None:
            n = self._size
        n = min(n, self._size)
        result = []
        for i in range(n):
            idx = (self._tail - 1 - i) % self._capacity
            result.append(self._buffer[idx])
        return result

    def get_pending(self) -> list:
        return [c for c in self.get_recent() if c.status == SyncChange.PENDING]

    def __len__(self):
        return self._size

    # raw slots untuk visualisasi
    def raw_slots(self):
        return list(self._buffer), self._head, self._tail, self._size


# ============================================================
# 5. NOTE APP
# ============================================================

class NoteApp:
    def __init__(self, buffer_capacity: int = 5):
        self._chrono_head = None
        self._chrono_tail = None
        self._alpha_head  = None
        self._alpha_tail  = None
        self._tag_map     = TagMap()
        self._sync_buffer = CircularBuffer(buffer_capacity)

    def _chrono_insert(self, note):
        if self._chrono_head is None:
            self._chrono_head = self._chrono_tail = note
        else:
            note.chrono_prev = self._chrono_tail
            self._chrono_tail.chrono_next = note
            self._chrono_tail = note

    def _alpha_insert(self, note):
        if self._alpha_head is None:
            self._alpha_head = self._alpha_tail = note
            return
        cur = self._alpha_head
        while cur is not None and cur.title.lower() < note.title.lower():
            cur = cur.alpha_next
        if cur is None:
            note.alpha_prev = self._alpha_tail
            self._alpha_tail.alpha_next = note
            self._alpha_tail = note
        elif cur is self._alpha_head:
            note.alpha_next = self._alpha_head
            self._alpha_head.alpha_prev = note
            self._alpha_head = note
        else:
            note.alpha_next = cur
            note.alpha_prev = cur.alpha_prev
            cur.alpha_prev.alpha_next = note
            cur.alpha_prev = note

    def _chrono_remove(self, note):
        if note.chrono_prev:
            note.chrono_prev.chrono_next = note.chrono_next
        else:
            self._chrono_head = note.chrono_next
        if note.chrono_next:
            note.chrono_next.chrono_prev = note.chrono_prev
        else:
            self._chrono_tail = note.chrono_prev
        note.chrono_prev = note.chrono_next = None

    def _alpha_remove(self, note):
        if note.alpha_prev:
            note.alpha_prev.alpha_next = note.alpha_next
        else:
            self._alpha_head = note.alpha_next
        if note.alpha_next:
            note.alpha_next.alpha_prev = note.alpha_prev
        else:
            self._alpha_tail = note.alpha_prev
        note.alpha_prev = note.alpha_next = None

    def add_note(self, title, content, tags=None):
        note = NoteNode(title, content)
        self._chrono_insert(note)
        self._alpha_insert(note)
        for tag in (tags or []):
            note.add_tag(tag)
            self._tag_map.add(tag, note)
        self._sync_buffer.push(SyncChange(note.id, 'ADD',
            {'title': title, 'content': content, 'tags': tags or []}))
        return note

    def edit_note(self, note, title=None, content=None, add_tags=None, remove_tags=None):
        if title and title != note.title:
            self._alpha_remove(note)
            note.title = title
            self._alpha_insert(note)
        if content:
            note.content = content
        for tag in (add_tags or []):
            note.add_tag(tag)
            self._tag_map.add(tag, note)
        for tag in (remove_tags or []):
            if tag in note.tags:
                note.tags.remove(tag)
            self._tag_map.remove(tag, note)
        self._sync_buffer.push(SyncChange(note.id, 'EDIT',
            {'title': note.title, 'content': note.content, 'tags': note.tags[:]}))

    def delete_note(self, note):
        self._chrono_remove(note)
        self._alpha_remove(note)
        for tag in note.tags:
            self._tag_map.remove(tag, note)
        self._sync_buffer.push(SyncChange(note.id, 'DEL', {'title': note.title}))

    def view_chronological(self):
        result, cur = [], self._chrono_head
        while cur:
            result.append(cur)
            cur = cur.chrono_next
        return result

    def view_alphabetical(self):
        result, cur = [], self._alpha_head
        while cur:
            result.append(cur)
            cur = cur.alpha_next
        return result

    def find_by_tag(self, tag):
        return self._tag_map.get_notes_by_tag(tag)

    def sync_status(self):
        return self._sync_buffer.get_recent()

    def pending_sync(self):
        return self._sync_buffer.get_pending()


# ============================================================
# VISUALISASI
# ============================================================

# Palet warna
C_PURPLE   = "#7F77DD"
C_PURPLE_L = "#EEEDFE"
C_TEAL     = "#1D9E75"
C_TEAL_L   = "#E1F5EE"
C_CORAL    = "#D85A30"
C_CORAL_L  = "#FAECE7"
C_AMBER    = "#BA7517"
C_AMBER_L  = "#FAEEDA"
C_GRAY     = "#888780"
C_GRAY_L   = "#F1EFE8"
C_BG       = "#FFFFFF"
C_TEXT     = "#2C2C2A"
C_MUTED    = "#5F5E5A"


def draw_node_box(ax, x, y, w, h, label, sublabel="", color=C_PURPLE_L,
                  border=C_PURPLE, fontsize=9, bold=False):
    """Gambar satu node box dengan label."""
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.03",
                         facecolor=color, edgecolor=border, linewidth=1)
    ax.add_patch(box)
    fw = 'bold' if bold else 'normal'
    ax.text(x, y + (0.06 if sublabel else 0), label,
            ha='center', va='center', fontsize=fontsize,
            fontweight=fw, color=C_TEXT)
    if sublabel:
        ax.text(x, y - 0.12, sublabel,
                ha='center', va='center', fontsize=7, color=C_MUTED)


def draw_arrow(ax, x1, y1, x2, y2, color=C_PURPLE, style='->', lw=1.2,
               curved=False, rad=0.0):
    """Gambar panah antara dua titik."""
    cs = f"arc3,rad={rad}" if curved else "arc3,rad=0"
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color,
                                lw=lw, connectionstyle=cs))


def fig1_dll_chains(notes_chrono, notes_alpha):
    """Gambar dua chain DLL (chronological & alphabetical)."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 5.5), facecolor=C_BG)
    fig.suptitle("① Doubly Linked List — Dua Chain per Node",
                 fontsize=13, fontweight='bold', color=C_TEXT, y=1.01)

    n = len(notes_chrono)
    W, H, GAP = 1.7, 0.55, 0.7   # lebar node, tinggi, jarak antar node

    for ax_idx, (ax, notes, title, color, color_l, color_arr_bwd) in enumerate([
        (axes[0], notes_chrono, "Chronological (urutan dibuat)",  C_PURPLE, C_PURPLE_L, C_GRAY),
        (axes[1], notes_alpha,  "Alphabetical (urutan judul A–Z)", C_TEAL,   C_TEAL_L,   C_GRAY),
    ]):
        ax.set_facecolor(C_BG)
        ax.set_xlim(-0.5, n * (W + GAP) + 0.5)
        ax.set_ylim(-0.6, 0.85)
        ax.axis('off')
        ax.text(0.01, 0.95, title, transform=ax.transAxes,
                fontsize=10, fontweight='bold', color=color, va='top')

        xs = [(i * (W + GAP) + W/2) for i in range(n)]

        # "head" label
        ax.text(xs[0], 0.62, "head", ha='center', fontsize=8,
                color=color, fontweight='bold')
        ax.annotate("", xy=(xs[0], 0.35), xytext=(xs[0], 0.55),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.2))
        # "tail" label
        ax.text(xs[-1], 0.62, "tail", ha='center', fontsize=8,
                color=color, fontweight='bold')
        ax.annotate("", xy=(xs[-1], 0.35), xytext=(xs[-1], 0.55),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.2))

        for i, note in enumerate(notes):
            x = xs[i]
            # Node box
            draw_node_box(ax, x, 0, W, H,
                          label=note.title,
                          sublabel=f"[{note.id}]",
                          color=color_l, border=color, fontsize=8)

            # Pointer .next (atas, ke kanan)
            if i < n - 1:
                draw_arrow(ax, x + W/2 - 0.05, 0.08,
                               xs[i+1] - W/2 + 0.05, 0.08,
                               color=color, lw=1.3)
            else:
                ax.text(x + W/2 + 0.08, 0.08, "∅",
                        ha='left', va='center', fontsize=9, color=C_MUTED)

            # Pointer .prev (bawah, ke kiri)
            if i > 0:
                draw_arrow(ax, x - W/2 + 0.05, -0.08,
                               xs[i-1] + W/2 - 0.05, -0.08,
                               color=color_arr_bwd, lw=1.0,
                               style='<-')
            else:
                ax.text(x - W/2 - 0.08, -0.08, "∅",
                        ha='right', va='center', fontsize=9, color=C_MUTED)

        # Legend
        ax.plot([], [], color=color,        lw=1.5, label='.next →')
        ax.plot([], [], color=color_arr_bwd, lw=1.0, label='.prev ←')
        ax.legend(loc='lower right', fontsize=8, framealpha=0.6)

    fig.tight_layout(pad=1.2)
    return fig


def fig2_tag_map(app, notes):
    """Gambar hash map tag → [notes]."""
    tags = app._tag_map.all_tags()
    if not tags:
        return None

    fig, ax = plt.subplots(figsize=(13, max(3.5, len(tags) * 0.9 + 1.5)),
                           facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.axis('off')
    ax.set_title("② TagMap — Hash Map: tag → list of NoteNode",
                 fontsize=13, fontweight='bold', color=C_TEXT, pad=10)

    # Posisi
    tag_x   = 1.5
    note_x0 = 4.5
    note_dx = 2.2
    row_h   = 0.9

    all_notes = {n.id: n for n in notes}

    for r, tag in enumerate(sorted(tags)):
        y = -(r * row_h)

        # Tag bucket
        draw_node_box(ax, tag_x, y, 2.2, 0.52,
                      label=f'"{tag}"', color=C_AMBER_L, border=C_AMBER,
                      fontsize=9, bold=True)

        tagged_notes = app.find_by_tag(tag)
        for c, note in enumerate(tagged_notes):
            nx = note_x0 + c * note_dx

            # Panah dari tag ke note
            if c == 0:
                ax.annotate("", xy=(nx - 0.9, y), xytext=(tag_x + 1.1, y),
                            arrowprops=dict(arrowstyle='->', color=C_AMBER, lw=1.2))
            else:
                # Panah antar note
                ax.annotate("", xy=(nx - 0.9, y),
                            xytext=(nx - note_dx + 0.9, y),
                            arrowprops=dict(arrowstyle='->', color=C_TEAL, lw=1.0))

            draw_node_box(ax, nx, y, 1.7, 0.48,
                          label=note.title, sublabel=f"[{note.id}]",
                          color=C_TEAL_L, border=C_TEAL, fontsize=8)

    ax.set_xlim(0, note_x0 + 5 * note_dx)
    ax.set_ylim(-(len(tags)) * row_h + 0.1, 0.7)
    fig.tight_layout(pad=1.5)
    return fig


def fig3_circular_buffer(app):
    """Gambar circular buffer sebagai lingkaran slot."""
    buf    = app._sync_buffer
    slots, head, tail, size = buf.raw_slots()
    cap    = buf._capacity

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("③ Circular Buffer — Sync Status Tracking",
                 fontsize=13, fontweight='bold', color=C_TEXT, pad=12)

    import math
    R = 1.8       # radius lingkaran slot
    SW = 1.5      # slot width (kotak)
    SH = 0.7      # slot height

    op_color = {'ADD': C_TEAL, 'EDIT': C_PURPLE, 'DEL': C_CORAL, None: C_GRAY}
    op_bg    = {'ADD': C_TEAL_L, 'EDIT': C_PURPLE_L, 'DEL': C_CORAL_L, None: C_GRAY_L}
    status_color = {
        SyncChange.PENDING: C_AMBER,
        SyncChange.SYNCED:  C_TEAL,
        SyncChange.FAILED:  C_CORAL,
        None: C_GRAY
    }

    cx, cy = 0, 0  # center

    for i in range(cap):
        angle = math.pi/2 - (2 * math.pi * i / cap)
        sx = cx + R * math.cos(angle)
        sy = cy + R * math.sin(angle)

        change = slots[i]
        is_head  = (i == head and size > 0)
        is_tail  = (i == (tail - 1) % cap and size > 0)
        is_empty = (change is None)

        op   = change.operation if change else None
        fc   = op_bg.get(op, C_GRAY_L)
        bc   = op_color.get(op, C_GRAY)
        lw   = 2.0 if (is_head or is_tail) else 1.0

        box = FancyBboxPatch((sx - SW/2, sy - SH/2), SW, SH,
                             boxstyle="round,pad=0.04",
                             facecolor=fc, edgecolor=bc, linewidth=lw)
        ax.add_patch(box)

        # Slot index
        ax.text(sx - SW/2 + 0.12, sy + SH/2 - 0.1,
                f"[{i}]", fontsize=7, color=C_MUTED, va='top')

        if is_empty:
            ax.text(sx, sy, "—", ha='center', va='center',
                    fontsize=11, color=C_GRAY)
        else:
            # Operasi
            ax.text(sx, sy + 0.15, change.operation,
                    ha='center', va='center', fontsize=9,
                    fontweight='bold', color=bc)
            # Note ID pendek
            ax.text(sx, sy - 0.05,
                    f"id:{change.note_id}",
                    ha='center', va='center', fontsize=7, color=C_TEXT)
            # Status badge
            sc = status_color.get(change.status, C_GRAY)
            ax.text(sx, sy - 0.22, change.status,
                    ha='center', va='center', fontsize=6.5,
                    color=sc, style='italic')

        # Label HEAD / TAIL
        label_r = R + 0.62
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        if is_head and is_tail:
            ax.text(lx, ly, "HEAD\n& TAIL", ha='center', va='center',
                    fontsize=7, color=C_AMBER, fontweight='bold')
        elif is_head:
            ax.text(lx, ly, "HEAD\n(oldest)", ha='center', va='center',
                    fontsize=7, color=C_AMBER, fontweight='bold')
        elif is_tail:
            ax.text(lx, ly, "next\nwrite", ha='center', va='center',
                    fontsize=7, color=C_PURPLE, fontweight='bold')

        # Panah antar slot (circular)
        next_angle = math.pi/2 - (2 * math.pi * (i + 1) / cap)
        nx2 = cx + (R - 0.05) * math.cos(next_angle)
        ny2 = cy + (R - 0.05) * math.sin(next_angle)
        mx  = cx + (R + 0.22) * math.cos((angle + next_angle) / 2)
        my  = cy + (R + 0.22) * math.sin((angle + next_angle) / 2)

        con = mpatches.FancyArrowPatch(
            (sx + (SW/2)*math.cos(angle - math.pi/2),
             sy + (SH/2)*math.sin(angle - math.pi/2)),
            (nx2 + (SW/2)*math.cos(next_angle + math.pi/2),
             ny2 + (SH/2)*math.sin(next_angle + math.pi/2)),
            connectionstyle=f"arc3,rad=0.35",
            arrowstyle='->', color=C_GRAY, lw=0.8, mutation_scale=8,
            alpha=0.5
        )
        ax.add_patch(con)

    # Keterangan kapasitas di tengah
    ax.text(cx, cy + 0.2, f"cap = {cap}", ha='center', va='center',
            fontsize=11, fontweight='bold', color=C_MUTED)
    ax.text(cx, cy - 0.15, f"size = {size}", ha='center', va='center',
            fontsize=10, color=C_MUTED)

    # Legend
    handles = [
        mpatches.Patch(fc=C_TEAL_L,   ec=C_TEAL,   label='ADD'),
        mpatches.Patch(fc=C_PURPLE_L, ec=C_PURPLE,  label='EDIT'),
        mpatches.Patch(fc=C_CORAL_L,  ec=C_CORAL,   label='DEL'),
        mpatches.Patch(fc=C_GRAY_L,   ec=C_GRAY,    label='kosong'),
    ]
    ax.legend(handles=handles, loc='lower center',
              bbox_to_anchor=(0.5, -0.08), ncol=4,
              fontsize=8, framealpha=0.6)

    margin = R + 1.3
    ax.set_xlim(cx - margin, cx + margin)
    ax.set_ylim(cy - margin, cy + margin)
    fig.tight_layout(pad=1.5)
    return fig


def fig4_overview(notes_chrono, app):
    """Gambar overview: semua node + kedua chain + tag connection."""
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.axis('off')
    ax.set_title("Overview Lengkap — NoteNode dengan Semua Koneksi",
                 fontsize=13, fontweight='bold', color=C_TEXT, pad=10)

    notes = notes_chrono
    n = len(notes)
    W, H = 1.8, 0.7
    GAP  = 0.6
    total_w = n * W + (n-1) * GAP
    x0 = (14 - total_w) / 2

    # Posisi x tiap node
    xs = [x0 + i * (W + GAP) + W/2 for i in range(n)]
    y_node = 2.8

    # Gambar setiap note node
    for i, note in enumerate(notes):
        x = xs[i]
        draw_node_box(ax, x, y_node, W, H,
                      label=note.title, sublabel=f"[{note.id}]",
                      color=C_PURPLE_L, border=C_PURPLE, fontsize=8)

        # Tag badges di bawah node
        for t_idx, tag in enumerate(note.tags):
            tx = x - (len(note.tags)-1)*0.4 + t_idx*0.8
            ty = y_node - 0.75
            bp = FancyBboxPatch((tx-0.35, ty-0.15), 0.7, 0.3,
                                boxstyle="round,pad=0.03",
                                facecolor=C_AMBER_L, edgecolor=C_AMBER, linewidth=0.7)
            ax.add_patch(bp)
            ax.text(tx, ty, tag, ha='center', va='center',
                    fontsize=6.5, color=C_AMBER)

    # Chain chronological (panah atas)
    for i in range(n-1):
        x1, x2 = xs[i], xs[i+1]
        # next (atas)
        ax.annotate("", xy=(x2 - W/2 + 0.05, y_node + 0.13),
                    xytext=(x1 + W/2 - 0.05, y_node + 0.13),
                    arrowprops=dict(arrowstyle='->', color=C_PURPLE, lw=1.3))
        # prev (kembali)
        ax.annotate("", xy=(x1 + W/2 - 0.05, y_node - 0.13),
                    xytext=(x2 - W/2 + 0.05, y_node - 0.13),
                    arrowprops=dict(arrowstyle='->', color=C_GRAY, lw=1.0))

    # Label chain chrono
    ax.text(xs[0] - W/2 - 0.15, y_node + 0.13, "chrono chain",
            ha='right', va='center', fontsize=8, color=C_PURPLE, fontstyle='italic')

    # Chain alphabetical (panah lebih bawah, warna teal)
    notes_alpha = sorted(notes, key=lambda n: n.title.lower())
    alpha_xs = {note.id: xs[notes.index(note)] for note in notes}

    y_alpha = y_node + 0.55
    for i in range(len(notes_alpha)-1):
        x1 = alpha_xs[notes_alpha[i].id]
        x2 = alpha_xs[notes_alpha[i+1].id]
        rad = 0.3 if abs(x2-x1) > W+GAP*2 else 0.0
        ax.annotate("", xy=(x2, y_alpha), xytext=(x1, y_alpha),
                    arrowprops=dict(arrowstyle='->',
                                   connectionstyle=f"arc3,rad={-rad}",
                                   color=C_TEAL, lw=1.2,
                                   linestyle='dashed'))

    ax.text(alpha_xs[notes_alpha[0].id] - W/2 - 0.15, y_alpha,
            "alpha chain", ha='right', va='center',
            fontsize=8, color=C_TEAL, fontstyle='italic')

    # Legend
    handles = [
        mpatches.Patch(fc=C_PURPLE_L, ec=C_PURPLE, label='Note node'),
        mpatches.Patch(fc=C_AMBER_L,  ec=C_AMBER,  label='Tag'),
        plt.Line2D([0],[0], color=C_PURPLE, lw=1.5, label='chrono .next →'),
        plt.Line2D([0],[0], color=C_GRAY,   lw=1.0, label='chrono .prev ←'),
        plt.Line2D([0],[0], color=C_TEAL,   lw=1.2,
                   linestyle='dashed', label='alpha chain →'),
    ]
    ax.legend(handles=handles, loc='lower left', bbox_to_anchor=(0, -0.04),
              ncol=5, fontsize=8, framealpha=0.7)

    ax.set_xlim(0, 14)
    ax.set_ylim(1.5, 4.0)
    fig.tight_layout(pad=1.5)
    return fig


# ============================================================
# MAIN — setup data, buat semua gambar, simpan ke PNG
# ============================================================

def main():
    app = NoteApp(buffer_capacity=5)

    n1 = app.add_note("Python Basics",    "Variabel, loop, fungsi",   tags=["python", "belajar"])
    n2 = app.add_note("Algoritma Sort",   "Bubble, merge, quick",     tags=["algoritma", "belajar"])
    n3 = app.add_note("Database SQL",     "SELECT, JOIN, index",       tags=["database", "sql"])
    n4 = app.add_note("Linked List",      "Singly, doubly, circular",  tags=["python", "algoritma"])
    n5 = app.add_note("Docker Intro",     "Container, image, compose", tags=["devops"])

    # Edit & delete untuk isi buffer
    app.edit_note(n1, title="Advanced Python", add_tags=["advanced"])
    app.delete_note(n5)

    # Mark beberapa sebagai synced
    for c in app.sync_status()[-2:]:
        c.mark_synced()

    notes_chrono = app.view_chronological()
    notes_alpha  = app.view_alphabetical()

    print("Membuat visualisasi...")

    f1 = fig1_dll_chains(notes_chrono, notes_alpha)
    p1 = os.path.join(BASE_DIR, "fig1_dll_chains.png")
    f1.savefig(p1, dpi=150, bbox_inches='tight', facecolor=C_BG)
    print(f"  ✓ fig1_dll_chains.png  →  {p1}")

    f2 = fig2_tag_map(app, notes_chrono)
    p2 = os.path.join(BASE_DIR, "fig2_tag_map.png")
    f2.savefig(p2, dpi=150, bbox_inches='tight', facecolor=C_BG)
    print(f"  ✓ fig2_tag_map.png     →  {p2}")

    f3 = fig3_circular_buffer(app)
    p3 = os.path.join(BASE_DIR, "fig3_circular_buffer.png")
    f3.savefig(p3, dpi=150, bbox_inches='tight', facecolor=C_BG)
    print(f"  ✓ fig3_circular_buffer.png  →  {p3}")

    f4 = fig4_overview(notes_chrono, app)
    p4 = os.path.join(BASE_DIR, "fig4_overview.png")
    f4.savefig(p4, dpi=150, bbox_inches='tight', facecolor=C_BG)
    print(f"  ✓ fig4_overview.png    →  {p4}")

    plt.close('all')
    print("\nSemua visualisasi selesai dibuat.")


if __name__ == "__main__":
    main()