from dataclasses import dataclass

@dataclass
class ConversationAnalysis:
    topic: str
    goal: str
    success: str