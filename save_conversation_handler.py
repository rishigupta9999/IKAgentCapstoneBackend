import json
from datetime import datetime, timezone
from dao.ConversationsDao import ConversationsDao
from model.Conversation import Conversation
from model.Turn import Turn

def lambda_handler(event, context):
    try:
        print("Received event: " + json.dumps(event, indent=2))
        
        # Handle direct invocation vs API Gateway
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event

        print(f"Body is {body}")

        turns = []

        for turn in body['turns']:
            print(f"Turn is {turn}")
            print(f"id is {turn['id']}")
            print(f"content is {turn['content']}")
            print(f"speaker is {turn['speaker']}")
            print(f"timestamp is {turn['timestamp']}")

            turns.append(Turn(
                id=turn['id'],
                content=turn['content'],
                speaker=turn['speaker'],
                timestamp=datetime.fromisoformat(turn['timestamp'].replace('Z', '+00:00')))
            )

        print(f"Deserialized turn {turns}")

        # Create conversation
        conversation = Conversation(
            conversation_id=body['conversation_id'],
            turns=turns,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
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
        print(f"Error: {e}")

        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }