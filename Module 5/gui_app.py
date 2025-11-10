import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from queue import Empty
import os
try:
    import winsound
except Exception:
    winsound = None

from messenger import ReliableMessenger
from CSV import _cleanup_csv
from header_bar import HeaderBar
from sidebar import Sidebar
from chat_view import ChatView
from input_bar import InputBar
from log_panel import LogPanel
from panels import AdminPanel, ChartsWindow, ServerLogWindow, LossSimulatorWindow

# Optional theming via ttkbootstrap (graceful fallback)
try:
    import ttkbootstrap as tb  # type: ignore
except Exception:
    tb = None


## NOTE: AdminPanel, ChartsWindow, ServerLogWindow are provided in panels.py


class ReliableStarGUI:
    def __init__(self, root: tk.Tk, messenger: ReliableMessenger):
        self.root = root
        self.messenger = messenger
        self.root.title("Reliable Messaging - Messenger GUI")
        self.root.geometry("980x720")
        self.root.configure(bg="#0b2239")

        self.style = None
        if tb is not None:
            try:
                self.style = tb.Style(theme="darkly")
            except Exception:
                self.style = None

        # Header
        self.header = HeaderBar(
            parent=self.root,
            messenger=self.messenger,
            on_verify=self._on_verify,
            on_toggle_log=self._toggle_log,
            on_help=self._open_help,
            on_strategy_select=self._on_strategy_select,
        )

        # Body split
        body = tk.Frame(self.root, bg="#0b2239")
        body.pack(side="top", fill="both", expand=True)

        # Sidebar
        actions = [
            ("Set Loss", self._on_set_loss),
            ("Chunk Size", self._on_set_chunk),
            ("Send Mode", self._on_set_strategy),
            ("Admin Panel", self._open_admin_panel),
            ("Charts", self._open_charts_panel),
            ("Server Log", self._show_server_log),
            ("Clear Screen", self._on_clear_screen),
            ("Clear CSV", self._on_clear_csv),
            ("Simulate Loss", self._open_loss_sim),
        ]
        self.sidebar = Sidebar(body, actions)

        # Content area: chat + input + log
        content = tk.Frame(body, bg="#0b2239")
        content.pack(side="left", fill="both", expand=True)
        self.chat = ChatView(content)
        self.input_var = tk.StringVar()
        self.input = InputBar(content, self.input_var, self._on_send, self._on_send_voice)
        self.log = LogPanel(content)

        # Timers
        self.root.after(250, self._poll_ui_queue)
        self.root.after(500, self._refresh_header_stats)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Welcome
        self.chat.append_notice(self.root, "Welcome - ⭐ delivered, ☆ lost/pending")

    # Timers
    def _refresh_header_stats(self):
        self.header.refresh_stats(self.messenger)
        self.root.after(500, self._refresh_header_stats)

    # Queue polling
    def _poll_ui_queue(self):
        try:
            msg, kind = self.messenger.ui_queue.get_nowait()
            if kind == "sent":
                self.chat.add_message(self.root, msg, "sent")
            elif kind == "recv":
                self.chat.add_message(self.root, msg, "recv")
            elif kind == "chunk":
                self.log.append(msg)
            elif kind == "notice":
                self.log.append(msg)
                self.chat.append_notice(self.root, msg)
            else:
                self.log.append(msg)
            self.messenger.ui_queue.task_done()
        except Empty:
            pass
        except Exception as e:
            try:
                self.log.append(f"[UI Error] {e}")
            except Exception:
                pass
        self.root.after(250, self._poll_ui_queue)

    # Header callbacks
    def _on_strategy_select(self, value: str):
        s = (value or "").strip().lower()
        if s == "single":
            self.messenger.set_strategy_single()
        elif s == "double":
            try:
                self.messenger.set_strategy_double()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot set double: {e}")
        elif s == "arq":
            r = simpledialog.askinteger("max_retries", "max_retries (>=0):", parent=self.root, minvalue=0)
            if r is None:
                self.header.reflect_strategy(self.messenger)
                return
            self.messenger.set_strategy_arq(r)
        else:
            messagebox.showerror("Error", "Invalid strategy.")
        self.header.reflect_strategy(self.messenger)

    def _toggle_log(self):
        self.log.toggle()

    def _open_help(self):
        text = (
            "Data Delivery System\n\n"
            "- Channel loss: Each attempt has a probability of loss sampled from the configured range.\n"
            "- Single: Send each chunk once.\n"
            "- Double: Send each chunk twice (improves delivery at cost of attempts).\n"
            "- ARQ (Stop-and-Wait): Retry lost chunks up to max_retries.\n\n"
            "Metrics\n"
            "- Chunks delivered vs total: overall reliability.\n"
            "- Attempts lost vs total: observed loss rate.\n"
            "- Loss range: configured per-send loss sampling bounds.\n"
        )
        win = tk.Toplevel(self.root)
        win.title("Help - Delivery System")
        txt = tk.Text(win, wrap="word", width=80, height=18)
        txt.pack(fill="both", expand=True)
        txt.insert("end", text)
        txt.configure(state="disabled")
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=6)

    # Actions/events
    def _on_send(self):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self.chat.add_message(self.root, f"You: {text}", "sent")
        self.messenger.send_message(text)

    def _on_send_voice(self):
        path = filedialog.askopenfilename(title="Select WAV file", filetypes=[["WAV files", "*.wav"], ["All files", "*.*"]], parent=self.root)
        if not path:
            return
        if not os.path.exists(path):
            messagebox.showerror("Voice", "Selected file does not exist.")
            return
        self.chat.add_voice(self.root, path, "sent", winsound=winsound)
        self.messenger.send_voice(path)

    def _on_verify(self):
        self.chat.append_notice(self.root, "[Server] Verifying...")
        complete, missing = self.messenger.verify_server()
        if complete:
            self.chat.append_notice(self.root, "[Result] OK - MESSAGE DELIVERED (all chunks arrived)")
            self.chat.mark_last_sent(True)
        else:
            self.chat.append_notice(self.root, f"[Result] X - MESSAGE INCOMPLETE (missing: {missing})")
            self.chat.mark_last_sent(False, "incomplete")

    def _on_set_loss(self):
        try:
            inp = simpledialog.askstring("Set Loss Range", "Enter min and max loss (e.g., 0.03 0.07):", parent=self.root)
            if inp is None:
                return
            parts = inp.strip().split()
            if len(parts) != 2:
                messagebox.showerror("Error", "Enter two numbers separated by space.")
                return
            a, b = float(parts[0]), float(parts[1])
            if not (0 <= a < b < 1):
                messagebox.showerror("Error", "Require 0 <= min < max < 1.")
                return
            self.messenger.set_loss_range(a, b)
        except Exception:
            messagebox.showerror("Error", "Invalid input. Use something like: 0.03 0.07")

    def _on_set_chunk(self):
        try:
            v = simpledialog.askinteger("Chunk size", "New chunk size (>=1):", parent=self.root, minvalue=1)
            if v is None:
                return
            self.messenger.set_chunk_size(v)
        except Exception:
            messagebox.showerror("Error", "Invalid integer.")

    def _on_set_strategy(self):
        choice = simpledialog.askstring("Strategy", "Enter 'single', 'double', or 'arq':", parent=self.root)
        if choice is None:
            return
        self._on_strategy_select(choice)

    def _on_clear_csv(self):
        self.messenger.clear_csv()

    def _on_clear_screen(self):
        for child in list(self.chat.inner.children.values()):
            try:
                child.destroy()
            except Exception:
                pass
        self.log.text.delete("1.0", "end")
        self.chat.append_notice(self.root, "Screen cleared.")

    def _open_admin_panel(self):
        AdminPanel(self.root, self.messenger)

    def _open_loss_sim(self):
        try:
            LossSimulatorWindow(self.root)
        except Exception:
            pass
    def _open_charts_panel(self):
        try:
            ChartsWindow(self.root)
        except Exception:
            pass

    def _show_server_log(self):
        if not self.messenger.server.log:
            messagebox.showinfo("Server Log", "(Server log is empty)")
            return
        ServerLogWindow(self.root, self.messenger.server.log)

    def _on_close(self):
        try:
            self.messenger.csv_file.close()
        except Exception:
            pass
        _cleanup_csv()
        self.root.destroy()


if __name__ == "__main__":
    messenger = ReliableMessenger()
    root = tk.Tk()
    gui = ReliableStarGUI(root, messenger)
    root.mainloop()


