import json
from datetime import datetime
from dao.ConversationsDao import ConversationsDao
from model.Conversation import Conversation
from model.Turn import Turn

def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        print("Received event: " + json.dumps(event, indent=2))
        
        # Handle direct invocation vs API Gateway
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Parse turns from request
        turns = [Turn(
            id=turn['id'],
            content=turn['content'],
            speaker=turn['speaker'],
            timestamp=datetime.fromisoformat(turn['timestamp'])
        ) for turn in body['turns']]
        
        # Create conversation
        conversation = Conversation(
            conversation_id=body['conversation_id'],
            turns=turns,
            created_at=datetime.fromisoformat(body['created_at']),
            updated_at=datetime.fromisoformat(body['updated_at'])
        )

        print("Successfully deserialized conversation")
        
        # Save to DynamoDB
        dao = ConversationsDao()
        dao.save_conversation(conversation)
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'message': 'Conversation saved successfully'})
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