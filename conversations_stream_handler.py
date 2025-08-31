import json
import logging
import os
from boto3.dynamodb.types import TypeDeserializer

from agent.sentiment import Sentiment
from model.Conversation import Conversation
from model.Turn import Turn
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
deserializer = TypeDeserializer()
def lambda_handler(event, context):
    """
    Lambda handler for DynamoDB stream events from the Conversations table.
    This is a placeholder implementation.
    """
    try:
        logger.info(f"Received DynamoDB stream event: {json.dumps(event)}")

        value = os.environ.get('ANTHROPIC_API_KEY')
        print(f"Anthropic API Key {value}")

        new_conversation = None

        # Process each record in the stream
        for record in event.get('Records', []):
            try:
                event_name = record.get('eventName')
                logger.info(f"Processing {event_name} event")
                logger.info(json.dumps(record))

                new_image = record['dynamodb']['NewImage']

                if new_image is not None:
                    new_conversation_json = dynamodb_to_json(new_image)
                    # Fix ConversationId field name mismatch
                    if 'ConversationId' in new_conversation_json:
                        new_conversation_json['conversation_id'] = new_conversation_json.pop('ConversationId')
                    
                    # Deserialize Turn objects
                    if 'turns' in new_conversation_json:
                        new_conversation_json['turns'] = [
                            Turn(
                                id=turn['id'],
                                content=turn['content'],
                                speaker=turn['speaker'],
                                timestamp=datetime.fromisoformat(turn['timestamp'])
                            ) for turn in new_conversation_json['turns']
                        ]
                    
                    new_conversation = Conversation(**new_conversation_json)

                logger.info(f"New Conversation: {new_conversation}")

                sentiment = Sentiment()
                logger.info("Successfully initiatlized sentiment")
                transcript = extract_transcript(new_conversation)
                sentiment.analyze(transcript)

                # Placeholder for stream processing logic
                # Add your business logic here
                
            except Exception as e:
                logger.error(f"Error processing record {record.get('eventName', 'unknown')}: {str(e)}")
                logger.error(f"Record data: {json.dumps(record)}")
                # Continue processing other records instead of failing the entire batch
                continue
        
        return {
            'statusCode': 200,
            'body': json.dumps('Stream processed successfully')
        }
        
    except Exception as e:
        logger.error(f"Fatal error in lambda_handler: {str(e)}")
        logger.error(f"Event data: {json.dumps(event)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing stream: {str(e)}')
        }

def extract_transcript(conversation):
    """Extract transcript from conversation turns as a single string"""
    return '\n'.join(turn.content for turn in conversation.turns)

def dynamodb_to_json(dynamodb_item):
    return {k: deserializer.deserialize(v) for k, v in dynamodb_item.items()}

