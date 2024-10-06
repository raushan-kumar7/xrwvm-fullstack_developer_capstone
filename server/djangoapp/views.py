from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Logger instance
logger = logging.getLogger(__name__)

# User login view
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    return JsonResponse({"userName": username, "status": "Failed"})

# User logout view
def logout_request(request):
    logout(request)
    return JsonResponse({"username": ""})

# User registration view
@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    
    try:
        User.objects.get(username=username)
        return JsonResponse({"userName": username, "error": "Already Registered"})
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})

# Retrieve car makes and models
def get_cars(request):
    if CarMake.objects.count() == 0:
        initiate()
    
    car_models = CarModel.objects.select_related('car_make')
    cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name} for car_model in car_models]
    
    return JsonResponse({"CarModels": cars})

# Retrieve dealerships
def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

# Retrieve dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        dealership = get_request(f"/fetchDealerById/{dealer_id}")
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 404})

# Retrieve dealer reviews
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        reviews = get_request(f"/reviews/dealer/{dealer_id}")
        for review_details in reviews:
            response = analyze_review_sentiments(review_details['review'])
            print(response)
            review_details['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    return JsonResponse({"status": 404})

# Add a review for a dealer
@csrf_exempt
def add_review(request):
    if request.method == "POST":
        data = json.loads(request.body)
        result = post_review(data)
        return JsonResponse(result)
