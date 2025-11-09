# EXPLANATION

This app simulates message delivery across a lossy channel and visualizes the process.

## Architecture
- GUI (Tkinter)
  - Events (send, verify, config) → `ReliableMessenger`
  - `ui_queue` used to push updates back to the GUI periodically
- Messaging Core
  - `ReliableMessenger` calls a chosen strategy in `Sending.py`
  - Strategy performs per‑chunk attempts via `NetworkChannel.transmit()`
  - `Server` accepts or rejects chunk delivery and verifies completeness
  - Each attempt is logged to `session_messages.csv`

## Data Flow
1. Message split into chunks (`Server.Message.chunks`) by `chunk_size`
2. For each chunk, the strategy attempts delivery (`Single`, `Double`, or `ARQ`)
3. Each attempt samples/uses loss (`NetworkChannel.transmit`) and records outcome
4. `Server.accept` marks chunk status; verification computes missing chunks
5. UI shows per‑chunk logs and delivery marks; summary panels and charts use CSV

## Strategies
- Single: one attempt per chunk; least overhead, most sensitive to loss
- Double: two attempts per chunk; improved delivery, more attempts
- Stop‑and‑Wait ARQ: retries per chunk up to `max_retries`; balances reliability vs attempts

## Concurrency
- Sending runs on a background thread
- GUI polls `ui_queue` every ~250ms to render updates without freezing

## Extensibility
- Add a strategy: implement a class with `send(msg, channel, server, writer, ui_emit, slow, loss_prob)` and plug it into `ReliableMessenger`
- Swap channel models: implement an object with `transmit()` that returns success/failure
