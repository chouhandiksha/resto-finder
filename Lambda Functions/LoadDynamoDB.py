import json
from decimal import Decimal
import boto3
import datetime
import urllib3
import urllib.request
import urllib.parse




cuisines = ['chinese','indian','italian','mexican','japanese', 'korean']


def lambda_handler(event, context):
    
    s3 = boto3.resource('s3')
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="https://dynamodb.us-west-2.amazonaws.com")
    table = dynamodb.Table('yelp-restaurants')
    
    content_object = s3.Object('mychatbotconcierge', 'yelp_data.json')
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    # for item in json_content:
    #     print("/n",item['businesses'][0])
    
    
 
    content_object = s3.Object('mychatbotconcierge', '{}.json'.format(cuisines[5]))
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    for item in json_content:
        businesses = item['businesses']
        for business in businesses:
                 details = {
                "insertedAtTimestamp": str(datetime.datetime.now()),
                "restaurant_id": business["id"],
                "alias": business["alias"],
                "name": business["name"],
                "rating": Decimal(business['rating']),
                "numReviews": int(business["review_count"]),
                "address": business["location"]["display_address"],
                "latitude": str(business["coordinates"]["latitude"]),
                "longitude": str(business["coordinates"]["longitude"]),
                "zip_code": business['location']['zip_code'],
                "cuisine": cuisines[5],
                "city:": business['location']['city']
                 }
                 table.put_item(Item=details)
        
    
    
   

            
    # table.put_item(Item=details)
#     for cuisine in cuisines:
#         restaurant_json = 
#         load_dynamo(restaurant_json, cuisine)




# def load_dynamo(response, cuisine):
#     new_response = json.loads(json.dumps(response), parse_float=Decimal)
#     counter = 0
#     for business in new_response["businesses"]:
#         keyCheck  = table.get_item(Key={'restaurantID':business['id']})
#         if 'Item' in keyCheck:
#             continue
#         try:
#             details = {
#                 "insertedAtTimestamp": str(datetime.datetime.now()),
#                 "restaurantID": business["id"],
#                 "alias": business["alias"],
#                 "name": business["name"],
#                 "rating": Decimal(business['rating']),
#                 "numReviews": int(business["review_count"]),
#                 "address": business["location"]["display_address"],
#                 "latitude": str(business["coordinates"]["latitude"]),
#                 "longitude": str(business["coordinates"]["longitude"]),
#                 "zip_code": business['location']['zip_code'],
#                 "cuisine": cuisine,
#                 "city:": business['location']['city']
#             }

#             table.put_item(Item=details)
#             counter = counter + 1

#         except Exception as e:
#             print("Error", e)
#             exit(1)
#     print(counter)