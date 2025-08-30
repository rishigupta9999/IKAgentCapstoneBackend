import json
import logging
import os
from boto3.dynamodb.types import TypeDeserializer

from agent.sentiment import Sentiment
from model.Conversation import Conversation

logger = logging.getLogger()
logger.setLevel(logging.INFO)
deserializer = TypeDeserializer()
def lambda_handler(event, context):
    """
    Lambda handler for DynamoDB stream events from the Conversations table.
    This is a placeholder implementation.
    """
    logger.info(f"Received DynamoDB stream event: {json.dumps(event)}")

    value = os.environ.get('ANTHROPIC_API_KEY')
    print(f"Anthropic API Key {value}")

    new_conversation = None

    # Process each record in the stream
    for record in event.get('Records', []):
        event_name = record.get('eventName')
        logger.info(f"Processing {event_name} event")
        logger.info(json.dumps(record))

        new_image = record['dynamodb']['NewImage']

        if new_image is not None:
            new_conversation_json = dynamodb_to_json(new_image)
            # Fix ConversationId field name mismatch
            if 'ConversationId' in new_conversation_json:
                new_conversation_json['conversation_id'] = new_conversation_json.pop('ConversationId')
            new_conversation = Conversation(**new_conversation_json)

        logger.info(f"New Conversation: {new_conversation}")

        sentiment = Sentiment()
        sentiment.analyze(new_conversation);

        # Placeholder for stream processing logic
        # Add your business logic here
    
    return {
        'statusCode': 200,
        'body': json.dumps('Stream processed successfully')
    }

def dynamodb_to_json(dynamodb_item):
    return {k: deserializer.deserialize(v) for k, v in dynamodb_item.items()}

