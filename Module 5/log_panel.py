import tkinter as tk


class LogPanel:
    def __init__(self, parent):
        self.visible = False
        self.container = tk.Frame(parent, bg="#0b2239")
        self.text = tk.Text(self.container, height=10, bg="#0a1a2b", fg="#e6f0ff", wrap="word", relief="flat", insertbackground="#e6f0ff")
        self.text.pack(fill="both", expand=True)

    def toggle(self):
        if self.visible:
            try:
                self.container.pack_forget()
            except Exception:
                pass
            self.visible = False
        else:
            self.container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self.visible = True

    def append(self, text: str):
        self.text.insert("end", text + "\n")
        self.text.see("end")

