import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChatLogs')

def lambda_handler(event, context):
    intent = event['currentIntent']['name']
    slots = event['currentIntent']['slots']
    session_id = event.get('sessionId', str(uuid.uuid4()))
    
    if intent == 'BookAppointment':
        name = slots.get('Name', 'User')
        date = slots.get('Date', 'N/A')
        
        if not date or date == 'N/A':
            return elicit_slot('Date', 'Please provide a valid date.', slots)
        
        # Store in DynamoDB
        table.put_item(Item={
            'SessionId': session_id,
            'UserName': name,
            'Date': date,
            'Query': intent,
            'Timestamp': context.get_remaining_time_in_millis()
        })
        
        response = f"Appointment booked for {name} on {date}!"
        return close_response(response)
    
    return close_response("Sorry, I didn't understand that.")

def elicit_slot(slot_to_elicit, message, slots):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'intent': {
                'name': 'BookAppointment',
                'slots': slots
            }
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }

def close_response(message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': 'BookAppointment',
                'state': 'Fulfilled'
            }
        },
        'messages': [{'contentType': 'PlainText', 'content': message}]
    }
