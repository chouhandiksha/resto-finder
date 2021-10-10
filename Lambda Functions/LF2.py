
import json
from requests_aws4auth import AWS4Auth
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
import random

def lambda_handler(event, context):
    
    host = "search-restaurants-tta6aypbynko652sp6l4mgmmka.us-west-2.es.amazonaws.com"
    region = "us-west-2"
    service = "es"
    
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth("AKIAZZ7HUOGP647BH67Y", "tO00Mqs7OUGCccK5/mZzIjyQh90NEvo8qRRxcu8L", region, service)
    
    #Dynamo db resource
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('yelp-restaurants')
    
    
    #ElasticSearch object
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    
    #SQS Resource
    sqs = boto3.resource("sqs")
    queue = sqs.get_queue_by_name(QueueName="SearchRestaurantQueue")
    print(queue)
    messages = queue.receive_messages(MessageAttributeNames=['All'])
    print(messages)
    #Retrieving details from the Queue
    for message in messages:
        msg_data=json.loads(message.body)
        location = str(msg_data['Location'])
        cuisine = str(msg_data['Cuisine'])
        time = str(msg_data['Time'])
        count = str(msg_data['Count'])
        email = str(msg_data['Email'])
            
            
        es_resultdata = es.search(index="restaurants", body={"query": {"match": {'cuisine':cuisine}}})
            
            
            
           
        
             
        #Generating Random outputs for selected details
        random_output = random.sample(es_resultdata['hits']['hits'], 3)
            
        db_response = [] 
        for x in random_output:
            db_response.append(table.get_item(
                        Key={
                            'restaurant_id': x['_source']['restaurant_id']
                        }
                    ) )  
               
                
            
            
            
        names = [] 
        address = []
            
        for i in range(3):
            names.append(db_response[i]['Item']['name'])
            address.append(' '.join(db_response[i]['Item']['address']))
            
                
        #email addresses    
        recipient_address = "dc4454@nyu.edu"
        sender_address = "dc4454@nyu.edu"
                    
        # The character encoding for the email.
        charset = "UTF-8"
                    
        #Region
        AWS_REGION = "us-west-2"
                
        # The subject line for the email.
        subject_email = "Dining Concierge Recommendations!"
              
        #The email body for recipients with non-HTML email clients.
        email_body = "You have selected the following details: Cuisine : {}, for {} People, at Time: {}\n".format(cuisine,count,time)+"\n We have the following recommendations for you!\n \n Restaurant Name: {} \n Restaurant Address: {} \n \n Restaurant Name: {} \n Restaurant Address: {} \n \n Restaurant Name: {} \n Restaurant Address: {} \n ".format(names[0], address[0],names[1], address[1],names[2], address[2])
            
                    
        #Create a new SES resource.
        client = boto3.client('ses',region_name=AWS_REGION)
                    
            
        #try send an email
                    
        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': [
              recipient_address,
                                  ],
                            },
                            Message={
                             'Body': {
                                 'Text': {
                                     'Charset': charset,
                                     'Data': email_body,
                                 },
                             },
                             'Subject': {
                                 'Charset': charset,
                                 'Data': subject_email,
                             },
                         },
                         Source=sender_address,
                            
                     )
                    
                    
                    
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
        message.delete()
    
        