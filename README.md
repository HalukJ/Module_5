# Module 5 – Reliable Messaging Simulator (Tkinter)

A desktop GUI that simulates reliable data delivery over a lossy channel. It offers three sending strategies (Single, Double, and Stop‑and‑Wait ARQ), live metrics, CSV logging, optional charts, and a small loss simulator. Built with Tkinter.

## Features
- Chat‑style GUI with delivery marks (pending, delivered, incomplete)
- Strategies: single, double, ARQ (configurable retries)
- Adjustable loss range and chunk size
- CSV logging of every attempt and Admin summary panel
- Optional charts (matplotlib) from session CSV
- Voice message support (WAV playback on Windows)

## Requirements
- Python 3.10+
- Optional: `ttkbootstrap` for theming, `matplotlib` for charts

## Quick Start
1) (Optional) Create/activate a virtual environment
2) Install optional deps if you want themes/charts:
   ```bash
   pip install ttkbootstrap matplotlib
   ```
3) Run the app:
   ```bash
   python "Module 5/main.py"
   ```

## Usage
- Pick a strategy in the header (Single, Double, ARQ). For ARQ you can set `max_retries` when prompted.
- Adjust loss range and chunk size from the sidebar.
- Send text or select a WAV file for a voice message.
- Click "Verify" to check delivery of the last message.
- Use "Admin Panel" and "Charts" for session metrics.
- "Clear Screen" resets the UI; "Clear CSV" resets session_messages.csv.

## Data & Artifacts
- `session_messages.csv` is created in the project root and holds per‑attempt logs.
- Bytecode caches under `__pycache__/` are ignored.

## Project Structure
- `Module 5/main.py` – App entry; wires `ReliableMessenger` to the GUI
- `Module 5/gui_app.py` – Main window composition and event wiring
- `Module 5/header_bar.py` – Strategy picker and live stats
- `Module 5/sidebar.py` – Actions (loss/chunk/strategy/admin/charts/log/clear)
- `Module 5/chat_view.py` – Message/voice bubbles and delivery marks
- `Module 5/input_bar.py` – Entry + Send/Voice buttons
- `Module 5/log_panel.py` – Toggleable debug log
- `Module 5/delivery_marks.py` – Delivery state symbols
- `Module 5/messenger.py` – Orchestration; threads, UI queue, CSV, strategies
- `Module 5/Sending.py` – Single, Double, Stop‑and‑Wait ARQ implementations
- `Module 5/Network.py` – Bernoulli loss channel
- `Module 5/Server.py` – Chunk tracking and verification
- `Module 5/CSV.py` – Session CSV lifecycle

## Notes
- CSV is cleaned up on exit/signals; you can also clear it from the sidebar.
- Charts require `matplotlib` and read `session_messages.csv` to render per‑message delivery rates.
