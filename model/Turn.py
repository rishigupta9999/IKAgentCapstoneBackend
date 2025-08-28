from dataclasses import dataclass
from datetime import datetime

@dataclass
class Turn:
    id: str  # UUID
    content: str
    speaker: str
    timestamp: datetime

