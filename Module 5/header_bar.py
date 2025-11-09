import tkinter as tk
from tkinter import ttk


class HeaderBar:
    def __init__(self, parent, messenger, on_verify, on_toggle_log, on_help, on_strategy_select):
        self.frame = tk.Frame(parent, bg="#08203a")
        self.frame.pack(side="top", fill="x")

        tk.Label(self.frame, text="Reliable Messenger", bg="#08203a", fg="#e6f0ff", font=("Segoe UI", 12, "bold")).pack(
            side="left", padx=10, pady=10
        )

        # Strategy quick selector
        self.strategy_var = tk.StringVar(value=getattr(messenger.strategy, 'name', 'arq'))
        ttk.Label(self.frame, text="Strategy:", background="#08203a", foreground="#c9dcff").pack(side="left")
        strategy_dd = ttk.Combobox(self.frame, textvariable=self.strategy_var, values=["single", "double", "arq"], width=8, state="readonly")
        strategy_dd.bind('<<ComboboxSelected>>', lambda e: on_strategy_select(self.strategy_var.get()))
        strategy_dd.pack(side="left", padx=(4, 12))

        # Live stats
        stats = tk.Frame(self.frame, bg="#08203a")
        stats.pack(side="left", padx=6)
        self.lbl_messages = tk.Label(stats, text="Msgs: 0", bg="#08203a", fg="#c9dcff", font=("Segoe UI", 9))
        self.lbl_messages.pack(side="left", padx=6)
        self.lbl_chunks = tk.Label(stats, text="Chunks: 0/0 (0%)", bg="#08203a", fg="#c9dcff", font=("Segoe UI", 9))
        self.lbl_chunks.pack(side="left", padx=6)
        self.lbl_attempts = tk.Label(stats, text="Attempts: 0 lost / 0 (0%)", bg="#08203a", fg="#c9dcff", font=("Segoe UI", 9))
        self.lbl_attempts.pack(side="left", padx=6)
        self.lbl_loss = tk.Label(stats, text=f"Loss: {messenger.loss_min:.0%}-{messenger.loss_max:.0%}", bg="#08203a", fg="#c9dcff", font=("Segoe UI", 9))
        self.lbl_loss.pack(side="left", padx=6)

        ttk.Button(self.frame, text="Help", command=on_help).pack(side="right", padx=8)
        ttk.Button(self.frame, text="Log", command=on_toggle_log).pack(side="right", padx=8)
        ttk.Button(self.frame, text="Verify", command=on_verify).pack(side="right")

    def reflect_strategy(self, messenger):
        try:
            self.strategy_var.set(getattr(messenger.strategy, 'name', 'arq'))
        except Exception:
            pass

    def refresh_stats(self, messenger):
        try:
            self.lbl_messages.configure(text=f"Msgs: {messenger.messages_sent}")
            total = max(1, messenger.total_chunks)
            delivered = messenger.delivered_total_chunks
            delivery_rate = (delivered / total) * 100.0
            self.lbl_chunks.configure(text=f"Chunks: {delivered}/{messenger.total_chunks} ({delivery_rate:.0f}%)")
            attempts = max(1, messenger.total_attempts)
            loss_rate = (messenger.total_lost_attempts / attempts) * 100.0
            self.lbl_attempts.configure(text=f"Attempts: {messenger.total_lost_attempts} lost / {messenger.total_attempts} ({loss_rate:.0f}%)")
            self.lbl_loss.configure(text=f"Loss: {messenger.loss_min:.0%}-{messenger.loss_max:.0%}")
        except Exception:
            pass

