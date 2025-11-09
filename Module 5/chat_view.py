import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from delivery_marks import DeliveryMarks


class ChatView:
    def __init__(self, parent):
        self.bubbles = []
        self.last_sent_index = None
        wrap = tk.Frame(parent, bg="#0b2239")
        wrap.pack(fill="both", expand=True, padx=10, pady=(8, 6))
        self.canvas = tk.Canvas(wrap, bg="#0b2239", highlightthickness=0)
        self.scroll = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.inner = tk.Frame(self.canvas, bg="#0b2239")
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

    def scroll_bottom(self, root):
        root.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def append_notice(self, root, text: str):
        row = tk.Frame(self.inner, bg="#0b2239")
        row.pack(fill="x", padx=6, pady=2)
        tk.Label(row, text=text, fg="#c9dcff", font=("Segoe UI", 9, "italic"), bg="#0b2239", wraplength=640, justify="center").pack(pady=2)
        self.scroll_bottom(root)

    def add_message(self, root, text: str, kind: str):
        timestamp = datetime.now().strftime("%H:%M")
        if kind == "sent":
            bg_color = "#157bb8"; fg_color = "#ffffff"; anchor = "e"; tick = DeliveryMarks.PENDING
        else:
            bg_color = "#ffffff"; fg_color = "#0b2239"; anchor = "w"; tick = ""
        row = tk.Frame(self.inner, bg="#0b2239"); row.pack(fill="x", padx=8, pady=4)
        inner = tk.Frame(row, bg="#0b2239"); inner.pack(anchor=anchor)
        txt = tk.Label(inner, text=text, bg=bg_color, fg=fg_color, font=("Segoe UI", 11), wraplength=560, justify="left", padx=12, pady=8, bd=0)
        txt.pack(side="top")
        meta = tk.Label(inner, text=DeliveryMarks.stamp(timestamp, tick), bg="#0b2239", fg="#c9dcff", font=("Segoe UI", 8))
        meta.pack(side="top", anchor="e", pady=(2, 0))
        info = {"kind": kind, "frame": row, "meta": meta, "text": txt}
        self.bubbles.append(info)
        if kind == "sent":
            self.last_sent_index = len(self.bubbles) - 1
        self.scroll_bottom(root)

    def add_voice(self, root, path: str, kind: str, winsound=None):
        fname = os.path.basename(path)
        label = f"Voice: {fname}"
        timestamp = datetime.now().strftime("%H:%M")
        if kind == "sent":
            bg_color = "#157bb8"; fg_color = "#ffffff"; anchor = "e"; tick = DeliveryMarks.PENDING
        else:
            bg_color = "#ffffff"; fg_color = "#0b2239"; anchor = "w"; tick = ""
        row = tk.Frame(self.inner, bg="#0b2239"); row.pack(fill="x", padx=8, pady=4)
        inner = tk.Frame(row, bg="#0b2239"); inner.pack(anchor=anchor)
        top = tk.Frame(inner, bg=bg_color); top.pack(side="top", anchor=anchor)
        txt = tk.Label(top, text=label, bg=bg_color, fg=fg_color, font=("Segoe UI", 11), padx=12, pady=8)
        txt.pack(side="left")
        def _play():
            if winsound and os.path.exists(path):
                try:
                    winsound.PlaySound(path, winsound.SND_FILENAME | getattr(winsound, 'SND_ASYNC', 0))
                except Exception:
                    messagebox.showinfo("Voice", f"Unable to play: {fname}")
            else:
                messagebox.showinfo("Voice", f"File not available: {fname}")
        ttk.Button(top, text="Play", command=_play).pack(side="left", padx=8)
        meta = tk.Label(inner, text=DeliveryMarks.stamp(timestamp, tick), bg="#0b2239", fg="#c9dcff", font=("Segoe UI", 8))
        meta.pack(side="top", anchor="e", pady=(2, 0))
        info = {"kind": kind, "frame": row, "meta": meta, "text": txt}
        self.bubbles.append(info)
        if kind == "sent":
            self.last_sent_index = len(self.bubbles) - 1
        self.scroll_bottom(root)

    def mark_last_sent(self, delivered: bool, detail: str = ""):
        if self.last_sent_index is None:
            return
        try:
            b = self.bubbles[self.last_sent_index]
            ts = b["meta"].cget("text").split(" ")[0]
            mark = DeliveryMarks.DELIVERED if delivered else DeliveryMarks.INCOMPLETE
            b["meta"].configure(text=DeliveryMarks.stamp(ts, mark if not detail else f"{mark} {detail}"))
        except Exception:
            pass

