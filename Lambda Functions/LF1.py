"""
This is an implementation of the Lex Code Hook Interface for diningSearchIntent Intent
which provides slot details.

"""

import json
import datetime
import time
import os
import dateutil.parser
import logging
import re
import boto3
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None



# def isvalid_car_type(car_type):
#     car_types = ['economy', 'standard', 'midsize', 'full size', 'minivan', 'luxury']
#     return car_type.lower() in car_types


def isvalid_city(city):
    valid_cities = ['manhattan', 'brooklyn', 'queens', 'bronx', 'long island']
    return city.lower() in valid_cities



# def isvalid_date(date):
#     try:
#         dateutil.parser.parse(date)
#         return True
#     except ValueError:
#         return False


def add_days(date, number_of_days):
    new_date = dateutil.parser.parse(date).date()
    new_date += datetime.timedelta(days=number_of_days)
    return new_date.strftime('%Y-%m-%d')


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
    
def validate_preferences(slots):
    
    food_list = ["italian", "indian", "chinese","mexican", "korean","japanese"]
    
    location = try_ex(lambda: slots['Location'])
    time = try_ex(lambda: slots['Time'])
    count = safe_int(try_ex(lambda: slots['Count']))
    cuisine = try_ex(lambda: slots['Cuisine'])
    email = try_ex(lambda: slots['Email'])
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    if cuisine and cuisine.lower() not in food_list:
        return build_validation_result(
            False,
            'Cuisine',
            'We could not find {} please enter valid cuisine type'.format(cuisine)
            )
    
    if location and not isvalid_city(location):
        return build_validation_result(
            False,
            'Location',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(location)
        )

    # if time:
    #     if !time.strptime(time_string[time, "%H:%M"]):
            # return build_validation_result(False, 'Time', 'I did not understand your check in time.  When would you like to check in?')
        # if datetime.datetime.strptime(checkin_date, '%Y-%m-%d').date() <= datetime.date.today():
        #     return build_validation_result(False, 'CheckInDate', 'Reservations must be scheduled at least one day in advance.  Can you try a different date?')

    if count is not None and (count < 1 or count > 20):
        return build_validation_result(
            False,
            'Count',
            'You can make a reservations for from one to twenty people.  How many people would be dining in?'
        )
    
     
    
    # if(!re.fullmatch(regex, email)):
    #     return build_validation_result(False, 'Email', 'Please type a valid email address.')

    return {'isValid': True}


""" --- Functions that control the bot's behavior --- """


def find_restaurant(intent_request):
   

    location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    time = try_ex(lambda: intent_request['currentIntent']['slots']['Time'])
    count = safe_int(try_ex(lambda: intent_request['currentIntent']['slots']['Count']))
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['Cuisine'])
    email = try_ex(lambda: intent_request['currentIntent']['slots']['Email'])
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    # session_attributes['currentPreferences'] = preferences

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_preferences(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        
        if location and count and time and cuisine and email:
            session_attributes['location'] = location
            session_attributes['cuisine'] = cuisine
            session_attributes['email'] = email
            session_attributes['count'] = count
            session_attributes['time'] = time

        
        return delegate(session_attributes, intent_request['currentIntent']['slots'])

    # Booking the hotel.  In a real application, this would likely involve a call to a backend service.
    # logger.debug('bookHotel under={}'.format(reservation))

    # try_ex(lambda: session_attributes.pop('currentReservationPrice'))
    # try_ex(lambda: session_attributes.pop('currentReservation'))
    # session_attributes['lastConfirmedReservation'] = reservation
    
    
    # Load search attributes with slot data
    preferences = json.dumps({
        'Location': location,
        'Count': count,
        'Time': time,
        'Cuisine': cuisine,
        'Email': email
    })
    # msg = {"Location" : location,"Count":count, "Time":time, "Cuisine": cuisine, "Email": email}

    
    QueueName = 'SearchRestaurantQueue'
    msg = send_sqs_message(QueueName,preferences)
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks, I have placed your query.   Please let me know if you would like to search anything else'
        }
    )

# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    # logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return find_restaurant(intent_request)
 

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    return dispatch(event)



def send_sqs_message(QueueName, msg_body):
    """

    :param sqs_queue_url: String URL of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    # Send the SQS message
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=QueueName)
   
    try:
        response = queue.send_message(MessageBody=msg_body)
        
    except ClientError as e:
        logging.error(e)
        return None
    return response