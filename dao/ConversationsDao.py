from dataclasses import asdict
from datetime import datetime
from typing import Optional, List
import boto3
from model.Conversation import Conversation
from model.Turn import Turn

class ConversationsDao:
    def __init__(self, table_name: str = "Conversations"):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save_conversation(self, conversation: Conversation) -> None:
        # Convert turns to dict and handle datetime serialization
        turns_data = []
        for turn in conversation.turns:
            turn_dict = asdict(turn)
            turn_dict['timestamp'] = turn.timestamp.isoformat()
            turns_data.append(turn_dict)
        
        item = {
            'ConversationId': conversation.conversation_id,
            'turns': turns_data,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        }
        self.table.put_item(Item=item)

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        response = self.table.get_item(Key={'ConversationId': conversation_id})
        if 'Item' not in response:
            return None

        item = response['Item']
        turns = [Turn(**turn) for turn in item['turns']]
        return Conversation(
            conversation_id=item['ConversationId'],
            turns=turns,
            created_at=datetime.fromisoformat(item['created_at']),
            updated_at=datetime.fromisoformat(item['updated_at'])
        )

    def get_all_conversations(self) -> List[Conversation]:
        response = self.table.scan()
        conversations = []
        
        for item in response['Items']:
            turns = []
            for turn_data in item['turns']:
                turn = Turn(
                    id=turn_data['id'],
                    content=turn_data['content'],
                    speaker=turn_data['speaker'],
                    timestamp=datetime.fromisoformat(turn_data['timestamp'])
                )
                turns.append(turn)
            
            conversation = Conversation(
                conversation_id=item['ConversationId'],
                turns=turns,
                created_at=datetime.fromisoformat(item['created_at']),
                updated_at=datetime.fromisoformat(item['updated_at'])
            )
            conversations.append(conversation)
        
        return conversations