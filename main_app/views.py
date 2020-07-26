from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from django.conf import settings
import json
import jsonify
import tweepy
import pickle
from .config import consumer_key, consumer_secret, access_token, access_token_secret

vectorizer = pickle.load(open('main_app/vectorizer.sav', 'rb'))
classifier = pickle.load(open('main_app/classifier.sav', 'rb'))

# Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)
        
def predict(text, include_neutral=True):
    text_vector = vectorizer.transform([text])
    # Predict
    result = classifier.predict(text_vector)
    if(result == 0):
        label = "Neutral"
    if(result == -1):
        label = "Negative"
    if(result == 1):
        label = "Positive"
    return {"label" : label}

def most_frequent(List): 
    counter = 0
    num = List[0] 
      
    for i in List: 
        curr_frequency = List.count(i) 
        if(curr_frequency> counter): 
            counter = curr_frequency 
            num = i 
    return num  

# Create your views here.
def homepage(request):
    return render(request, "build/index.html")

@api_view(["GET"])
def getsentiment(request):
    data = {"success": False}
    # if parameters are found, echo the msg parameter 
    if (request.data != None):       
    	data["predictions"] = predict(request.GET.get("text"))
    	data["success"] = True
    return JsonResponse(data)

@api_view(["GET"])
def analyzehashtag(request):
    positive = 0
    neutral = 0
    negative = 0
    for tweet in tweepy.Cursor(api.search,q="" + request.GET.get("text") + " -filter:retweets",rpp=5,lang="id", tweet_mode='extended').items(150):
        prediction = predict(tweet.full_text)
        if(prediction["label"] == "Positive"):
            positive += 1
        if(prediction["label"] == "Neutral"):
            neutral += 1
        if(prediction["label"] == "Negative"):
            negative += 1
    return JsonResponse({"positive": positive, "neutral": neutral, "negative": negative});

@api_view(["GET"])
def gettweets(request):
    tweets = []
    for tweet in tweepy.Cursor(api.search,q="" + request.GET.get("text") + " -filter:retweets",rpp=5,lang="id", tweet_mode='extended').items(150):
        temp = {}
        temp["text"] = tweet.full_text
        temp["username"] = tweet.user.screen_name
        temp["usercount"] = most_frequent(temp["username"])
        prediction = predict(tweet.full_text)
        temp["label"] = prediction["label"]
        tweets.append(temp)
    return JsonResponse({"results": tweets});
