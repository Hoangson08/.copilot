"""
Thời khóa biểu tự động - Python + tkinter (không cần cài thêm thư viện).
Chạy: python thoi_khoa_bieu.py
"""
import json
import os
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import messagebox, ttk

SESSION = 45          # phút mỗi buổi học
SHORT_BREAK = 10      # nghỉ ngắn
LONG_BREAK = 20       # nghỉ dài sau mỗi 3 buổi
NUM_SUBJECTS = 7
DAYS = ["Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]
COLORS = ["#2563eb", "#db2777", "#059669", "#d97706", "#7c3aed", "#0891b2", "#dc2626"]
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tkb_data.json")

DEMO = [
    ("Toán", ["Hàm số bậc hai", "Phương trình lượng giác", "Tích phân cơ bản", "Xác suất"]),
    ("Vật lý", ["Dao động điều hòa", "Sóng cơ", "Dòng điện xoay chiều"]),
    ("Hóa học", ["Este - lipit", "Cacbohiđrat", "Polime"]),
    ("Tiếng Anh", ["Thì hiện tại hoàn thành", "Câu điều kiện", "Từ vựng Unit 5"]),
    ("Ngữ văn", ["Tây Tiến", "Việt Bắc"]),
    ("Sinh học", ["Di truyền quần thể", "Tiến hóa"]),
    ("Lịch sử", ["Chiến dịch Điện Biên Phủ", "Thời kỳ Đổi mới"]),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Thời khóa biểu tự động")
        self.geometry("1100x680")
        self.minsize(900, 560)
        self.plan = []          # list các ngày, mỗi ngày là list các buổi học
        self.done = set()       # các bài đã học xong
        self.iid_key = {}       # iid của Treeview -> key bài học
        self.rows = []          # (entry tên môn, text bài học)
        self.build_ui()
        self.load()

    # ---------- Giao diện ----------
    def build_ui(self):
        left = ttk.Frame(self, padding=10)
        left.pack(side="left", fill="y")
        right = ttk.Frame(self, padding=10)
        right.pack(side="left", fill="both", expand=True)

        top = ttk.Frame(left)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Số giờ học/ngày:").grid(row=0, column=0, sticky="w")
        self.hours = tk.StringVar(value="2")
        ttk.Spinbox(top, from_=0.5, to=12, increment=0.5, width=6,
                    textvariable=self.hours).grid(row=0, column=1, padx=6)
        ttk.Label(top, text="Giờ bắt đầu (HH:MM):").grid(row=1, column=0, sticky="w", pady=4)
        self.start = tk.StringVar(value="18:00")
        ttk.Entry(top, width=8, textvariable=self.start).grid(row=1, column=1, padx=6)

        for i in range(NUM_SUBJECTS):
            box = tk.Frame(left, highlightthickness=2, highlightbackground=COLORS[i])
            box.pack(fill="x", pady=3)
            name = ttk.Entry(box)
            name.pack(fill="x", padx=4, pady=(4, 2))
            text = tk.Text(box, height=3, width=34, wrap="word")
            text.pack(fill="x", padx=4, pady=(0, 4))
            self.rows.append((name, text))
        ttk.Label(left, text="Mỗi dòng trong ô dưới tên môn là một bài cần học.",
                  foreground="#666").pack(anchor="w")

        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="Tạo thời khóa biểu", command=self.generate).pack(side="left", fill="x", expand=True)
        ttk.Button(btns, text="Dữ liệu mẫu", command=self.fill_demo).pack(side="left", padx=4)
        ttk.Button(btns, text="Xóa hết", command=self.clear).pack(side="left")

        self.progress_label = ttk.Label(right, text="Chưa có lịch. Nhập môn học và bấm “Tạo thời khóa biểu”.")
        self.progress_label.pack(anchor="w")
        self.bar = ttk.Progressbar(right, maximum=100)
        self.bar.pack(fill="x", pady=4)
        ttk.Label(right, text="Bấm đúp vào một bài để đánh dấu đã học xong.",
                  foreground="#666").pack(anchor="w")

        cols = ("time", "subject", "lesson", "done")
        self.tree = ttk.Treeview(right, columns=cols, show="tree headings")
        self.tree.heading("#0", text="Ngày")
        self.tree.heading("time", text="Giờ")
        self.tree.heading("subject", text="Môn")
        self.tree.heading("lesson", text="Bài học")
        self.tree.heading("done", text="Xong")
        self.tree.column("#0", width=190, stretch=False)
        self.tree.column("time", width=110, stretch=False)
        self.tree.column("subject", width=120, stretch=False)
        self.tree.column("lesson", width=280)
        self.tree.column("done", width=60, anchor="center", stretch=False)
        for i, c in enumerate(COLORS):
            self.tree.tag_configure(f"s{i}", foreground=c)
        self.tree.tag_configure("done", foreground="#999")
        scroll = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, pady=6)
        scroll.pack(side="left", fill="y", pady=6)
        self.tree.bind("<Double-1>", self.toggle)

    # ---------- Logic xếp lịch ----------
    def read_subjects(self):
        subjects = []
        for i, (name, text) in enumerate(self.rows):
            n = name.get().strip()
            lessons = [x.strip() for x in text.get("1.0", "end").splitlines() if x.strip()]
            if n and lessons:
                subjects.append({
                    "idx": i, "name": n,
                    "lessons": [{"sub": i, "name": n, "lesson": l, "key": f"{i}|{j}|{l}"}
                                for j, l in enumerate(lessons)],
                })
        return subjects

    def generate(self):
        subjects = self.read_subjects()
        if not subjects:
            messagebox.showinfo("Thiếu dữ liệu", "Hãy nhập ít nhất một môn học kèm một bài cần học.")
            return
        try:
            hours = float(self.hours.get().replace(",", "."))
            datetime.strptime(self.start.get().strip(), "%H:%M")
        except ValueError:
            messagebox.showerror("Sai định dạng", "Số giờ phải là số, giờ bắt đầu dạng HH:MM (ví dụ 18:00).")
            return

        # Xen kẽ các môn để không học một môn liên tục
        queue, r, more = [], 0, True
        while more:
            more = False
            for s in subjects:
                if r < len(s["lessons"]):
                    queue.append(s["lessons"][r])
                    more = True
            r += 1

        per_day = max(1, round(hours * 60 / SESSION))
        self.plan = [queue[k:k + per_day] for k in range(0, len(queue), per_day)]
        self.done &= {it["key"] for it in queue}
        self.render()
        self.save()

    def render(self):
        self.tree.delete(*self.tree.get_children())
        self.iid_key.clear()
        start_t = datetime.strptime(self.start.get().strip(), "%H:%M")
        total = done = 0
        for d, day in enumerate(self.plan):
            dt = date.today() + timedelta(days=d)
            minutes = len(day) * SESSION
            label = f"{DAYS[dt.weekday()]}, {dt:%d/%m}" + (" (hôm nay)" if d == 0 else "")
            parent = self.tree.insert("", "end", iid=f"d{d}", text=label, open=True,
                                      values=(f"{minutes // 60}h{minutes % 60:02d} học", "", "", ""))
            t = datetime.combine(dt, start_t.time())
            for j, it in enumerate(day):
                end = t + timedelta(minutes=SESSION)
                is_done = it["key"] in self.done
                total += 1
                done += is_done
                iid = f"d{d}s{j}"
                self.iid_key[iid] = it["key"]
                tags = ("done",) if is_done else (f"s{it['sub']}",)
                self.tree.insert(parent, "end", iid=iid, text="",
                                 values=(f"{t:%H:%M} - {end:%H:%M}", it["name"], it["lesson"],
                                         "✔" if is_done else ""), tags=tags)
                gap = LONG_BREAK if (j + 1) % 3 == 0 else SHORT_BREAK
                t = end + timedelta(minutes=gap)
        pct = done / total * 100 if total else 0
        self.bar["value"] = pct
        self.progress_label.config(
            text=f"Đã học {done}/{total} bài - {len(self.plan)} ngày, mỗi buổi {SESSION} phút, "
                 f"nghỉ {SHORT_BREAK} phút (nghỉ dài {LONG_BREAK} phút sau mỗi 3 buổi)")

    def toggle(self, event):
        iid = self.tree.identify_row(event.y)
        key = self.iid_key.get(iid)
        if not key:
            return
        self.done ^= {key}
        self.render()
        self.save()

    # ---------- Tiện ích ----------
    def fill_demo(self):
        self.clear(ask=False)
        for (name, text), (n, lessons) in zip(self.rows, DEMO):
            name.insert(0, n)
            text.insert("1.0", "\n".join(lessons))
        self.hours.set("2")
        self.start.set("18:00")
        self.generate()

    def clear(self, ask=True):
        if ask and not messagebox.askyesno("Xóa hết", "Xóa toàn bộ môn học và lịch?"):
            return
        for name, text in self.rows:
            name.delete(0, "end")
            text.delete("1.0", "end")
        self.done.clear()
        self.plan = []
        self.tree.delete(*self.tree.get_children())
        self.bar["value"] = 0
        self.progress_label.config(text="Chưa có lịch. Nhập môn học và bấm “Tạo thời khóa biểu”.")
        self.save()

    def save(self):
        data = {
            "hours": self.hours.get(), "start": self.start.get(),
            "subjects": [[n.get(), t.get("1.0", "end").strip()] for n, t in self.rows],
            "done": sorted(self.done),
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def load(self):
        try:
            with open(SAVE_FILE, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        self.hours.set(data.get("hours", "2"))
        self.start.set(data.get("start", "18:00"))
        for (name, text), (n, l) in zip(self.rows, data.get("subjects", [])):
            name.insert(0, n)
            text.insert("1.0", l)
        self.done = set(data.get("done", []))
        if self.read_subjects():
            self.generate()


if __name__ == "__main__":
    App().mainloop()