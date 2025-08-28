import json
from dao.ConversationsDao import ConversationsDao

def lambda_handler(event, context):
    try:
        dao = ConversationsDao()
        conversations = dao.get_all_conversations()
        
        # Convert conversations to JSON-serializable format
        conversations_data = []
        for conversation in conversations:
            conversation_dict = {
                'conversation_id': conversation.conversation_id,
                'turns': [
                    {
                        'id': turn.id,
                        'content': turn.content,
                        'speaker': turn.speaker,
                        'timestamp': turn.timestamp.isoformat()
                    }
                    for turn in conversation.turns
                ],
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            }
            conversations_data.append(conversation_dict)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps(conversations_data)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }