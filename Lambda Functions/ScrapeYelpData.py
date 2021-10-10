import json
import requests
import time

ans = []


def lambda_handler(event, context):
    scrape_yelp_data()
url = "https://api.yelp.com/v3/businesses/search"
api_key = "-M9TV5cDWd1Y9Svqc9u9dpZrx-fVhQdDlUDjmK46lKLpjkk2HuNSxxWS0WiDKjFhQXueEpm6gUH28pjrZfX1Z2YqIx-vM-ej319Evh0JY845jyHXzKWJ0VXe0R5MYXYx"
def search(cuisine, offset):
    url_params = {
        'location': 'new york',
        'offset' : offset,
        'limit': 50,
        'term': cuisine + " restaurants",
        'sort_by' : 'rating'
    }
    
    headers = {'Authorization': 'Bearer {}'.format(api_key)}
    
    
    
    response = requests.get(url, headers=headers, params=url_params)
    rjson = response.json()
    
    return rjson
    

def scrape_yelp_data(event=None, context=None):
    cuisines=['indian', 'mexican', 'chinese', 'italian', 'japanese', 'korean']
    for cuisine in cuisines:
        for x in range(0,1000,50):
            ans.append(search(cuisine, x))
        
    return json.dumps(ans)
            
res = scrape_yelp_data()
print(res)