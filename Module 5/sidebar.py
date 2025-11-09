import tkinter as tk
from tkinter import ttk


class Sidebar:
    def __init__(self, parent, actions):
        frame = tk.Frame(parent, bg="#091a2e", width=240)
        frame.pack(side="left", fill="y")
        frame.pack_propagate(False)
        tk.Label(frame, text="Chats", bg="#091a2e", fg="#c9dcff", anchor="w", font=("Segoe UI", 11, "bold")).pack(fill="x", padx=12, pady=(12, 6))
        chat_list = tk.Listbox(frame, activestyle="none", height=8, bg="#0a1f36", fg="#e6f0ff", selectbackground="#134e7a", borderwidth=0, highlightthickness=0)
        chat_list.pack(fill="x", padx=12)
        chat_list.insert("end", "Server")
        chat_list.selection_set(0)
        tk.Label(frame, text="Actions", bg="#091a2e", fg="#c9dcff", anchor="w", font=("Segoe UI", 11, "bold")).pack(fill="x", padx=12, pady=(16, 6))
        btns = tk.Frame(frame, bg="#091a2e")
        btns.pack(fill="x", padx=10, pady=(0, 10))
        for text, cmd in actions:
            ttk.Button(btns, text=text, command=cmd).pack(fill="x", pady=3)

