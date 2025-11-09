import tkinter as tk


class InputBar:
    def __init__(self, parent, input_var: tk.StringVar, on_send, on_voice):
        self.frame = tk.Frame(parent, bg="#0b2239")
        self.frame.pack(fill="x", padx=10, pady=(0, 10))
        self.entry = tk.Entry(self.frame, textvariable=input_var, font=("Segoe UI", 12), relief="solid", bd=1, bg="#fff8d6", highlightthickness=0, insertbackground="#333333")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=9)
        self.entry.bind("<Return>", lambda e: on_send())
        tk.Button(self.frame, text="Send", command=on_send, bg="#00c853", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=8, activebackground="#00a844").pack(side="left")
        tk.Button(self.frame, text="Voice", command=on_voice, bg="#2196f3", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=8, activebackground="#1976d2").pack(side="left", padx=6)

    def focus(self):
        try:
            self.entry.focus_set()
        except Exception:
            pass

