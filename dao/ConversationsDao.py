from dataclasses import asdict, fields
from datetime import datetime
from typing import Optional, List
import logging
import boto3
from model.Conversation import Conversation
from model.Turn import Turn
from model.ConversationAnalysis import ConversationAnalysis

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ConversationsDao:
    def __init__(self, table_name: str = "Conversations"):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save_conversation(self, conversation: Conversation) -> None:
        item = self._serialize_conversation(conversation)
        self.table.put_item(Item=item)

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        response = self.table.get_item(Key={'ConversationId': conversation_id})
        if 'Item' not in response:
            return None
        return self._deserialize_conversation(response['Item'])

    def get_all_conversations(self) -> List[Conversation]:
        response = self.table.scan()
        return [self._deserialize_conversation(item) for item in response['Items']]

    def update_conversation_analysis(self, conversation_id: str, analysis: ConversationAnalysis) -> None:
        self.table.update_item(
            Key={'ConversationId': conversation_id},
            UpdateExpression='SET conversation_analysis = :analysis',
            ExpressionAttributeValues={':analysis': asdict(analysis)}
        )

        logging.info(f"Updated analysis for conversation {conversation_id}")
    
    def _serialize_conversation(self, conversation: Conversation) -> dict:
        item = asdict(conversation)
        item['ConversationId'] = item.pop('conversation_id')
        
        # Convert datetime objects to ISO strings
        for turn in item['turns']:
            if isinstance(turn['timestamp'], datetime):
                turn['timestamp'] = turn['timestamp'].isoformat()
        
        if isinstance(item['created_at'], datetime):
            item['created_at'] = item['created_at'].isoformat()
        if isinstance(item['updated_at'], datetime):
            item['updated_at'] = item['updated_at'].isoformat()
            
        return item
    
    def _deserialize_conversation(self, item: dict) -> Conversation:
        # Handle turns
        turns = [self._deserialize_turn(turn_data) for turn_data in item['turns']]
        
        # Build kwargs for Conversation, handling field mapping
        kwargs = {'conversation_id': item['ConversationId'], 'turns': turns}
        
        # Dynamically handle all other fields
        conversation_fields = {f.name for f in fields(Conversation)}
        for key, value in item.items():
            if key == 'ConversationId' or key == 'turns':
                continue
            
            field_name = key
            if field_name in conversation_fields:
                if field_name in ['created_at', 'updated_at'] and isinstance(value, str):
                    kwargs[field_name] = datetime.fromisoformat(value)
                elif field_name == 'conversation_analysis' and value:
                    kwargs[field_name] = ConversationAnalysis(**value)
                else:
                    kwargs[field_name] = value
        
        return Conversation(**kwargs)
    
    def _deserialize_turn(self, turn_data: dict) -> Turn:
        kwargs = dict(turn_data)
        if 'timestamp' in kwargs and isinstance(kwargs['timestamp'], str):
            kwargs['timestamp'] = datetime.fromisoformat(kwargs['timestamp'])
        return Turn(**kwargs)