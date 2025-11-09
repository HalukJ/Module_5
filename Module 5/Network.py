#kayıp yapabilen kod
#attığımız zar

import random
from typing import Optional

class NetworkChannel:
    """Bernoulli per-attempt loss."""

    def __init__(self, loss_prob: float, rng: Optional[random.Random] = None):
        if not (0.0 <= loss_prob < 1.0):
            raise ValueError("loss_prob must be in [0, 1)")
        self.p = loss_prob
        self.rng = rng or random.Random()

    def transmit(self) -> bool:
        return self.rng.random() >= self.p
