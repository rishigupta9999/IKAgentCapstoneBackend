import json
import logging
import os
from boto3.dynamodb.types import TypeDeserializer

from agent.sentiment import Sentiment, State
from agent.summarizer import Summarizer
from dao.ConversationsDao import ConversationsDao
from model.Conversation import Conversation
from model.ConversationAnalysis import ConversationAnalysis
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

        # Process each record in the stream
        for record in event.get('Records', []):
            try:
                event_name = record.get('eventName')
                logger.info(f"Processing {event_name} event")
                logger.info(json.dumps(record))

                new_image = record['dynamodb'].get('NewImage')
                old_image = record['dynamodb'].get('OldImage')

                new_conversation = deserialize_conversation(new_image) if new_image else None
                old_conversation = deserialize_conversation(old_image) if old_image else None

                # Skip processing if turns are identical
                if turns_are_identical(old_conversation, new_conversation):
                    logger.info("Skipping processing - turns are identical")
                    continue

                if new_conversation:
                    logger.info(f"New Conversation: {new_conversation}")
                    
                    sentiment = Sentiment()
                    logger.info("Successfully initialized sentiment")

                    transcript = extract_transcript(new_conversation)
                    sentiment_state = sentiment.analyze(transcript)

                    summarizer = Summarizer()
                    summary = summarizer.analyze(transcript)
                    logger.info(f"Generated summary {summary}")

                    dao = ConversationsDao()
                    dao.update_conversation_analysis(new_conversation.conversation_id, sentiment_state_to_conversation_analysis(sentiment_state))
                    dao.update_summary(new_conversation.conversation_id, summary)

                if old_conversation:
                    logger.info(f"Old Conversation: {old_conversation}")
                
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

def deserialize_conversation(dynamodb_image):
    """Deserialize DynamoDB image to Conversation object"""
    if not dynamodb_image:
        return None
    
    conversation_json = dynamodb_to_json(dynamodb_image)
    # Fix ConversationId field name mismatch
    if 'ConversationId' in conversation_json:
        conversation_json['conversation_id'] = conversation_json.pop('ConversationId')
    
    # Deserialize Turn objects
    if 'turns' in conversation_json:
        conversation_json['turns'] = [
            Turn(
                id=turn['id'],
                content=turn['content'],
                speaker=turn['speaker'],
                timestamp=datetime.fromisoformat(turn['timestamp'])
            ) for turn in conversation_json['turns']
        ]
    
    return Conversation(**conversation_json)

def turns_are_identical(old_conversation, new_conversation):
    """Deep compare turns between old and new conversations"""
    if not old_conversation or not new_conversation:
        return False
    
    old_turns = old_conversation.turns
    new_turns = new_conversation.turns
    
    if len(old_turns) != len(new_turns):
        return False
    
    for old_turn, new_turn in zip(old_turns, new_turns):
        if (old_turn.id != new_turn.id or 
            old_turn.content != new_turn.content or 
            old_turn.speaker != new_turn.speaker or 
            old_turn.timestamp != new_turn.timestamp):
            return False
    
    return True

def sentiment_state_to_conversation_analysis(state):
    analysis = ConversationAnalysis(state['topic'], state['goal'], state['success'])

    return analysis