#mesajı atıp sonra gittimi diye kontrol ettiğimiz yer

import time
from Server import Message, Server
from Network import NetworkChannel

class SingleSend:
    name = "single"

    def send(self, msg: Message, channel: NetworkChannel, server: Server, writer,
             ui_emit, slow: float, loss_prob: float):
        attempts = 0
        lost_attempts = 0
        for idx, _payload in enumerate(msg.chunks(), start=1):
            attempts += 1
            ok = channel.transmit()
            symbol = "★" if ok else "☆"
            ui_emit(f"  chunk {idx}: {symbol}", "chunk")
            server.accept(idx, ok)
            writer.writerow([time.time(), msg.id, idx, 1, "delivered" if ok else "lost", symbol, "single", loss_prob])
            if not ok:
                lost_attempts += 1
            if slow > 0:
                time.sleep(slow * 5)
        return attempts, lost_attempts

class StopAndWaitARQ:
    name = "arq"

    def __init__(self, max_retries: int = 2):
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self.max_retries = max_retries

    def send(self, msg: Message, channel: NetworkChannel, server: Server, writer,
             ui_emit, slow: float, loss_prob: float):
        attempts = 0
        lost_attempts = 0
        for idx, _payload in enumerate(msg.chunks(), start=1):
            delivered = False
            attempt = 0
            while attempt <= self.max_retries and not delivered:
                attempt += 1
                attempts += 1
                ok = channel.transmit()
                if ok:
                    ui_emit(f"  chunk {idx} attempt {attempt}: ★", "chunk")
                    server.accept(idx, True)
                    writer.writerow([time.time(), msg.id, idx, attempt, "delivered", "★", "arq", loss_prob])
                    delivered = True
                else:
                    ui_emit(f"  chunk {idx} attempt {attempt}: ☆ (retrying)", "chunk")
                    server.accept(idx, False)
                    writer.writerow([time.time(), msg.id, idx, attempt, "lost", "☆", "arq", loss_prob])
                    lost_attempts += 1
                    if slow > 0:
                        time.sleep(slow * 3)
            if not delivered:
                ui_emit(f"  chunk {idx}: ☆ (retry limit exceeded)", "chunk")
                server.accept(idx, False)
                writer.writerow([time.time(), msg.id, idx, attempt, "failed", "☆", "arq-limit", loss_prob])
        return attempts, lost_attempts

class DoubleSend:
    name = "double"

    def send(self, msg: Message, channel: NetworkChannel, server: Server, writer,
             ui_emit, slow: float, loss_prob: float):
        attempts = 0
        lost_attempts = 0
        for idx, _payload in enumerate(msg.chunks(), start=1):
            delivered = False
            # Attempt 1
            attempts += 1
            ok1 = channel.transmit()
            if ok1:
                ui_emit(f"  chunk {idx} attempt 1: ✓", "chunk")
                server.accept(idx, True)
                writer.writerow([time.time(), msg.id, idx, 1, "delivered", "✓", "double-1", loss_prob])
                delivered = True
            else:
                ui_emit(f"  chunk {idx} attempt 1: ✗ (trying second)", "chunk")
                server.accept(idx, False)
                writer.writerow([time.time(), msg.id, idx, 1, "lost", "✗", "double-1", loss_prob])
                lost_attempts += 1
                if slow > 0:
                    time.sleep(slow * 2)

            # Attempt 2 always performed (double send)
            attempts += 1
            ok2 = channel.transmit()
            if ok2:
                ui_emit(f"  chunk {idx} attempt 2: ✓", "chunk")
                server.accept(idx, True)
                writer.writerow([time.time(), msg.id, idx, 2, "delivered", "✓", "double-2", loss_prob])
                delivered = True or delivered
            else:
                ui_emit(f"  chunk {idx} attempt 2: ✗", "chunk")
                server.accept(idx, False)
                writer.writerow([time.time(), msg.id, idx, 2, "lost", "✗", "double-2", loss_prob])
                lost_attempts += 1
                if slow > 0:
                    time.sleep(slow * 2)

            if not delivered:
                ui_emit(f"  chunk {idx}: ✗ (both attempts failed)", "chunk")
        return attempts, lost_attempts
