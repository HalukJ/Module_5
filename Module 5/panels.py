import csv
import tkinter as tk
from tkinter import ttk, messagebox
from CSV import SESSION_CSV
from Network import NetworkChannel
import random


class AdminPanel(tk.Toplevel):
    def __init__(self, root: tk.Tk, messenger):
        super().__init__(root)
        self.title("Admin Panel - Deliveries")
        self.configure(bg="#0b2239")
        self.geometry("540x380")
        self.messenger = messenger

        toolbar = tk.Frame(self, bg="#0b2239")
        toolbar.pack(fill="x", padx=8, pady=8)
        ttk.Button(toolbar, text="Refresh", command=self._refresh).pack(side="left")
        ttk.Button(toolbar, text="Close", command=self.destroy).pack(side="right")

        self.content = tk.Frame(self, bg="#0b2239")
        self.content.pack(fill="both", expand=True)
        self._refresh()

    def _metric(self, label, value):
        row = tk.Frame(self.content, bg="#0b2239")
        row.pack(fill="x", padx=10, pady=6)
        tk.Label(row, text=label, width=22, anchor="w", bg="#0b2239", fg="#c9dcff", font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(row, text=value, anchor="w", bg="#0b2239", fg="#ffffff", font=("Segoe UI", 11)).pack(side="left")

    def _refresh(self):
        for child in self.content.winfo_children():
            child.destroy()
        m = self.messenger
        delivered = m.delivered_total_chunks
        total = max(1, m.total_chunks)
        attempts = max(1, m.total_attempts)
        loss_rate = (m.total_lost_attempts / attempts) * 100.0
        delivery_rate = (delivered / total) * 100.0
        self._metric("Messages sent", str(m.messages_sent))
        self._metric("Chunks delivered", f"{delivered} / {m.total_chunks} ({delivery_rate:.1f}%)")
        self._metric("Attempts lost", f"{m.total_lost_attempts} / {m.total_attempts}")
        self._metric("Loss rate", f"{loss_rate:.1f}%")
        self._metric("Strategy", getattr(m.strategy, "name", type(m.strategy).__name__))
        self._metric("Chunk size", str(m.chunk_size))
        self._metric("Loss range", f"{m.loss_min:.2%} - {m.loss_max:.2%}")


class ChartsWindow(tk.Toplevel):
    def __init__(self, root: tk.Tk):
        try:
            import matplotlib
            matplotlib.use("Agg")
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.pyplot as plt
        except Exception:
            messagebox.showerror("Charts", "matplotlib is not installed. Please install it to view charts.")
            raise

        super().__init__(root)
        self.title("Charts - Delivery Rates")
        self.geometry("800x420")
        container = tk.Frame(self, bg="#0b2239")
        container.pack(fill="both", expand=True)

        per_message = {}
        attempts_total = 0
        attempts_lost = 0
        try:
            with open(SESSION_CSV, newline="", encoding="utf-8") as f:
                r = csv.DictReader(f)
                last_status = {}
                for row in r:
                    mid = int(row.get("message_id", 0))
                    idx = int(row.get("chunk_index", 0))
                    status = (row.get("status") or "").strip().lower()
                    key = (mid, idx)
                    last_status[key] = status
                    attempts_total += 1
                    if status in {"lost", "failed"}:
                        attempts_lost += 1
                for (mid, idx), status in last_status.items():
                    per_message.setdefault(mid, {"delivered": 0, "total": 0})
                    per_message[mid]["total"] += 1
                    if status == "delivered":
                        per_message[mid]["delivered"] += 1
        except FileNotFoundError:
            messagebox.showinfo("Charts", "No session CSV found yet.")
            self.destroy()
            return
        except Exception as e:
            messagebox.showerror("Charts", f"Could not read CSV: {e}")
            self.destroy()
            return

        mids = sorted(per_message.keys())
        if not mids:
            messagebox.showinfo("Charts", "No data to chart yet.")
            self.destroy()
            return
        rates = [(per_message[m]["delivered"] / max(1, per_message[m]["total"])) * 100.0 for m in mids]
        loss_rate = (attempts_lost / max(1, attempts_total)) * 100.0

        fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=100)
        ax.bar([str(m) for m in mids], rates, color="#1dd760")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Delivery Rate %")
        ax.set_xlabel("Message ID")
        ax.set_title(f"Per-Message Delivery Rate (overall loss ~ {loss_rate:.1f}%)")
        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class ServerLogWindow(tk.Toplevel):
    def __init__(self, root: tk.Tk, log_lines):
        super().__init__(root)
        self.title("Server Log")
        text = tk.Text(self, wrap="word", width=80, height=20)
        text.pack(fill="both", expand=True)
        for line in log_lines or []:
            text.insert("end", f"{line}\n")
        text.configure(state="disabled")
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=4)


class LossSimulatorWindow(tk.Toplevel):
    def __init__(self, root: tk.Tk, default_min=0.1, default_max=0.3):
        super().__init__(root)
        self.title("Packet Loss Simulator")
        self.geometry("720x420")

        ctrl = tk.Frame(self)
        ctrl.pack(fill="x", padx=8, pady=8)

        tk.Label(ctrl, text="Chunks:").pack(side="left")
        self.var_chunks = tk.IntVar(value=10)
        tk.Entry(ctrl, textvariable=self.var_chunks, width=6).pack(side="left", padx=(4, 10))

        tk.Label(ctrl, text="Attempts/Chunk:").pack(side="left")
        self.var_attempts = tk.IntVar(value=1)
        tk.Entry(ctrl, textvariable=self.var_attempts, width=6).pack(side="left", padx=(4, 10))

        tk.Label(ctrl, text="Loss range (min max):").pack(side="left")
        self.var_min = tk.DoubleVar(value=default_min)
        self.var_max = tk.DoubleVar(value=default_max)
        tk.Entry(ctrl, textvariable=self.var_min, width=6).pack(side="left", padx=(4, 2))
        tk.Entry(ctrl, textvariable=self.var_max, width=6).pack(side="left", padx=(2, 10))

        ttk.Button(ctrl, text="Run", command=self._run).pack(side="right")

        self.text = tk.Text(self, wrap="none")
        self.text.pack(fill="both", expand=True)

    def _run(self):
        try:
            n_chunks = max(1, int(self.var_chunks.get()))
            attempts_per = max(1, int(self.var_attempts.get()))
            lo = float(self.var_min.get()); hi = float(self.var_max.get())
            if not (0 <= lo < hi < 1):
                raise ValueError("loss range must satisfy 0 <= min < max < 1")
        except Exception as e:
            messagebox.showerror("Simulator", f"Invalid input: {e}")
            return

        self.text.delete("1.0", "end")
        rng = random.Random()
        loss = rng.uniform(lo, hi)
        ch = NetworkChannel(loss_prob=loss, rng=rng)
        lost_attempts = 0
        total_attempts = 0
        delivered_chunks = 0

        self.text.insert("end", f"Using fixed loss={loss:.1%} across {n_chunks} chunks, {attempts_per} attempt(s)/chunk\n\n")
        for idx in range(1, n_chunks + 1):
            row = [f"chunk {idx:02d}:"]
            delivered = False
            for a in range(1, attempts_per + 1):
                total_attempts += 1
                ok = ch.transmit()
                if ok:
                    row.append("✓")
                    delivered = True
                else:
                    row.append("✗")
                    lost_attempts += 1
            if delivered:
                delivered_chunks += 1
            self.text.insert("end", " ".join(row) + "\n")

        self.text.insert("end", "\nSummary:\n")
        self.text.insert("end", f"  Chunks delivered: {delivered_chunks}/{n_chunks} ({delivered_chunks/n_chunks*100:.1f}%)\n")
        self.text.insert("end", f"  Attempts lost: {lost_attempts}/{total_attempts} ({lost_attempts/max(1,total_attempts)*100:.1f}%)\n")
