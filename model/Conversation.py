from dataclasses import dataclass
from datetime import datetime
from typing import List
from .Turn import Turn
from .ConversationAnalysis import ConversationAnalysis

@dataclass
class Conversation:
    conversation_id: str
    turns: List[Turn]
    created_at: datetime
    updated_at: datetime
    conversation_analysis: ConversationAnalysis = None
    summary: str = None
    compliance: str = None