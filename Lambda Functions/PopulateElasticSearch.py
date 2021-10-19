import json
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import boto3
def lambda_handler(event, context):
    # TODO implement
    host = "search-restaurants-tta6aypbynko652sp6l4mgmmka.us-west-2.es.amazonaws.com"
    region = "us-west-2"
    service = "es"
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth("key", "value", region, service)
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    print(es)
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('yelp-restaurants')
    response = table.scan()
    for business in response['Items']:
        restaurant_id = business["restaurant_id"]
        cuisine = business["cuisine"]
        print(restaurant_id, cuisine)
        doc = {
            "restaurant_id": restaurant_id,
            "cuisine": cuisine
            }
        es.index(
            index="restaurants",
            doc_type="Restaurant",
            id=restaurant_id,
            body=doc)
        check = es.get(index="restaurants", doc_type="Restaurant", id=restaurant_id)
        if check["found"]:
            print("Index %s succeeded" % restaurant_id)
   
    # restaurantID = response['Items'][0]["restaurant_id"]
    # cuisine = response['Items'][0]["cuisine"]
    # doc = {
    #             "restaurant_id": restaurantID,
    #             "cuisine": cuisine
    #         }
    # es.index(
    #             index="restaurants",
    #             doc_type="Restaurant",
    #             id=restaurantID,
    #             body=doc,
    #         )
    # check = es.get(index="restaurants", doc_type="Restaurant", id=restaurantID)
    # print(check["found"])
