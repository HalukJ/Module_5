# iki cihaz arasÄ± etkileÅŸimi simÃ¼le ettiÄŸimiz yer
import random
import threading
import queue
from Server import Message, Server
from Network import NetworkChannel
from Sending import SingleSend, StopAndWaitARQ, DoubleSend
from CSV import open_csv_writer, SESSION_CSV, _cleanup_csv

SLOW_DELAY = 0.03

class ReliableMessenger:
    def __init__(self, writer=None, csv_file=None, slow_delay=SLOW_DELAY):
        self.server = Server()
        self.strategy = StopAndWaitARQ(max_retries=2)
        self.chunk_size = 5
        self.slow_delay = slow_delay
        self.loss_min = 0.03
        self.loss_max = 0.07
        self.message_id_counter = 0

        self.total_chunks = 0
        self.total_attempts = 0
        self.total_lost_attempts = 0
        self.delivered_total_chunks = 0
        self.results_history = []
        self.last_loss = None
        self.messages_sent = 0

        # CSV
        if writer and csv_file:
            self.writer = writer
            self.csv_file = csv_file
        else:
            self.writer, self.csv_file = open_csv_writer()

        # UI queue for communicating with GUI
        self.ui_queue = queue.Queue()

    # -----------------------
    # UI communication
    # -----------------------
    def ui_emit(self, text: str, kind: str = "recv"):
        self.ui_queue.put((text, kind))

    # -----------------------
    # Channel & loss
    # -----------------------
    def sampled_loss(self) -> float:
        return random.uniform(self.loss_min, self.loss_max)

    def make_channel(self, current_loss: float) -> NetworkChannel:
        return NetworkChannel(loss_prob=current_loss, rng=random.Random())

    # -----------------------
    # Message sending
    # -----------------------
    def send_message(self, text: str):
        self.message_id_counter += 1
        msg = Message(id=self.message_id_counter, text=text, chunk_size=self.chunk_size)
        t = threading.Thread(target=self._worker_send_message, args=(msg,), daemon=True)
        t.start()
        return msg

    # -----------------------
    # Voice sending (file-based)
    # -----------------------
    def send_voice(self, file_path: str):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except Exception as e:
            self.ui_emit(f"[Voice Error] Cannot read file: {e}", "notice")
            return None

        class _VoiceMsg:
            def __init__(self, id, data: bytes, chunk_size: int):
                self.id = id
                self.data = data
                self.chunk_size = chunk_size
            def chunks(self):
                n = max(1, self.chunk_size)
                return [self.data[i:i+n] for i in range(0, len(self.data), n)]

        self.message_id_counter += 1
        msg = _VoiceMsg(self.message_id_counter, data, self.chunk_size)
        t = threading.Thread(target=self._worker_send_voice, args=(msg,), daemon=True)
        t.start()
        return msg

    def _worker_send_voice(self, msg):
        chunks = msg.chunks()
        current_loss = self.sampled_loss()
        self.last_loss = current_loss
        self.ui_emit(f"[Client] Sending voiceâ€¦ (loss={current_loss:.2%})", "notice")
        self.server.reset()
        self.server.start(len(chunks))
        self.total_chunks += len(chunks)
        ch = self.make_channel(current_loss)
        try:
            attempts, losts = self.strategy.send(msg, ch, self.server, self.writer, self.ui_emit, self.slow_delay, current_loss)
            self.total_attempts += attempts
            self.total_lost_attempts += losts
            try: self.csv_file.flush()
            except Exception: pass
            self.ui_emit("[Client] Voice done. Use 'Verify Server' to check delivery.", "notice")
            try:
                self.results_history.append({
                    "id": msg.id,
                    "type": "voice",
                    "strategy": getattr(self.strategy, "name", type(self.strategy).__name__),
                    "loss": current_loss,
                    "chunks": len(chunks),
                    "attempts": attempts,
                    "lost_attempts": losts,
                })
            except Exception:
                pass
        except Exception as e:
            self.ui_emit(f"[Error] Voice sending failed: {e}", "notice")

    def _worker_send_message(self, msg: Message):
        chunks = msg.chunks()
        current_loss = self.sampled_loss()
        self.last_loss = current_loss
        self.ui_emit(f"[Client] Sendingâ€¦ (loss={current_loss:.2%})", "notice")
        self.server.reset()
        self.server.start(len(chunks))
        self.total_chunks += len(chunks)
        ch = self.make_channel(current_loss)
        try:
            attempts, losts = self.strategy.send(msg, ch, self.server, self.writer, self.ui_emit, self.slow_delay, current_loss)
            self.total_attempts += attempts
            self.total_lost_attempts += losts
            try: self.csv_file.flush()
            except Exception: pass
            self.ui_emit("[Client] Done. Use 'Verify Server' to check delivery.", "notice")
        except Exception as e:
            self.ui_emit(f"[Error] Sending failed: {e}", "notice")

    # -----------------------
    # Server verification
    # -----------------------
    def verify_server(self):
        complete, missing = self.server.verify()
        delivered_now = sum(1 for v in self.server.received.values() if v)
        self.delivered_total_chunks += delivered_now
        self.messages_sent += 1
        try:
            self.results_history.append({
                "id": self.message_id_counter,
                "type": "last",
                "complete": complete,
                "delivered_chunks": delivered_now,
                "expected_chunks": len(self.server.received) or 0,
                "missing": list(missing),
                "strategy": getattr(self.strategy, "name", type(self.strategy).__name__),
            })
        except Exception:
            pass
        return complete, missing

    # -----------------------
    # Strategy & configuration
    # -----------------------
    def set_loss_range(self, min_loss: float, max_loss: float):
        self.loss_min = min_loss
        self.loss_max = max_loss
        self.ui_emit(f"[Config] Loss range set to [{min_loss:.2%}, {max_loss:.2%}]", "notice")

    def set_chunk_size(self, size: int):
        self.chunk_size = size
        self.ui_emit(f"[Config] Chunk size set to {size}", "notice")

    def set_strategy_single(self):
        self.strategy = SingleSend()
        self.ui_emit("[Config] Strategy set to SINGLE", "notice")

    def set_strategy_arq(self, max_retries: int):
        self.strategy = StopAndWaitARQ(max_retries)
        self.ui_emit(f"[Config] Strategy set to ARQ (max_retries={max_retries})", "notice")

    def set_strategy_double(self):
        self.strategy = DoubleSend()
        self.ui_emit("[Config] Strategy set to DOUBLE", "notice")

    # -----------------------
    # Experiment
    # -----------------------
    def run_experiment(self, n: int = 20):
        t = threading.Thread(target=self._worker_experiment, args=(n,), daemon=True)
        t.start()

    def _worker_experiment(self, auto_n: int):
        try:
            self.ui_emit(f"[Experiment] Sending {auto_n} messagesâ€¦", "notice")
            exp_delivered_chunks = 0
            exp_total_chunks = 0
            exp_attempts = 0
            exp_lost_attempts = 0
            for k in range(1, auto_n + 1):
                text = f"Hello #{k} - automated test message"
                self.message_id_counter += 1
                msg = Message(id=self.message_id_counter, text=text, chunk_size=self.chunk_size)
                chunks = msg.chunks()
                current_loss = self.sampled_loss()
                self.last_loss = current_loss
                self.ui_emit(f"  â†’ Msg {k:02d}: using loss={current_loss:.2%}", "notice")
                self.server.reset()
                self.server.start(len(chunks))
                exp_total_chunks += len(chunks)
                ch = self.make_channel(current_loss)
                attempts, losts = self.strategy.send(msg, ch, self.server, self.writer, self.ui_emit, 0.0, current_loss)
                exp_attempts += attempts
                exp_lost_attempts += losts
                got_now = sum(1 for v in self.server.received.values() if v)
                exp_delivered_chunks += got_now

            self.delivered_total_chunks += exp_delivered_chunks
            self.total_chunks += exp_total_chunks
            self.total_attempts += exp_attempts
            self.total_lost_attempts += exp_lost_attempts
            self.messages_sent += auto_n

            self.ui_emit("[Experiment Summary]", "notice")
            self.ui_emit(f"  Messages: {auto_n}", "notice")
            self.ui_emit(f"  Chunks: delivered={exp_delivered_chunks} / total={exp_total_chunks}", "notice")
            self.ui_emit(f"  Attempts: lost={exp_lost_attempts} / total={exp_attempts}", "notice")
            try: self.csv_file.flush()
            except Exception: pass
        except Exception as e:
            self.ui_emit(f"[Experiment Error] {e}", "notice")

    # -----------------------
    # CSV management
    # -----------------------
    def clear_csv(self):
        import os
        try:
            if os.path.exists(SESSION_CSV):
                os.remove(SESSION_CSV)
            self.writer, self.csv_file = open_csv_writer()
            self.ui_emit("[CSV] Cleared session CSV", "notice")
        except Exception as e:
            self.ui_emit(f"[CSV Error] {e}", "notice")


