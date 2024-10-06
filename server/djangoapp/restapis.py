import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5050/")

# Function for making GET requests to the backend
def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params += f"{key}={value}&"
    
    request_url = f"{backend_url}{endpoint}?{params}"
    print(f"GET from {request_url}")
    
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")

# Function for analyzing review sentiments
def analyze_review_sentiments(text):
    request_url = f"{sentiment_analyzer_url}analyze/{text}"
    
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")

# Function for posting reviews
def post_review(data_dict):
    request_url = f"{backend_url}/insert_review"
    
    try:
        response = requests.post(request_url, json=data_dict)
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")
