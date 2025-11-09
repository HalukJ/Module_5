

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Message:#Parçalara ayırıyor
    id: int
    text: str
    chunk_size: int

    def chunks(self) -> List[str]:
        n = max(1, self.chunk_size)
        s = self.text
        if len(s) == 0:
            return [""]
        return [s[i: i + n] for i in range(0, len(s), n)]

class Server:#gelen mesajları kontrol ediyor doğruluyor
    def __init__(self):
        self.expected: int = 0
        self.received: Dict[int, bool] = {}
        self.log: List[str] = []

    def reset(self):
        self.expected = 0
        self.received = {}
        self.log = []

    def start(self, expected_chunks: int):
        self.expected = expected_chunks
        self.received = {i: False for i in range(1, expected_chunks + 1)}
        self.log.append(f"Server ready: expecting {expected_chunks} chunks")

    def accept(self, chunk_index: int, ok: bool):
        if ok and chunk_index in self.received:
            self.received[chunk_index] = True
            self.log.append(f"★ chunk {chunk_index} stored")
        else:
            self.log.append(f"☆ chunk {chunk_index} missing")

    def verify(self) -> Tuple[bool, List[int]]:
        if not self.received:
            self.log.append("☆ message INCOMPLETE (no chunks)")
            return False, []
        complete = all(self.received.values())
        missing = [i for i, v in self.received.items() if not v]
        self.log.append("★ message COMPLETE" if complete else f"☆ message INCOMPLETE (missing: {missing})")
        return complete, missing
