#!env python

import json
import pandas
import matplotlib.pyplot as plt
import sys
import string
import threading

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from twitterkey import TwitterKey

access_token = TwitterKey.access_token
access_token_secret = TwitterKey.access_token_secret
consumer_key = TwitterKey.consumer_key
consumer_secret = TwitterKey.consumer_secret

class StdOutListener(StreamListener):
    period = 1
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.tweets_per_period = 0
        self.timer = threading.Timer(self.period, self.printTweetCountAndReset)
        self.timer.start()
        
    def on_data(self, data):
        self.tweets_per_period += 1
        
        decoded_json = json.loads(data)
        #print decoded_json.keys()
        #print decoded_json["user"]["id"]
        try:
            screen_name = decoded_json["user"]["screen_name"]
            pass
        except KeyError:
            print "++++++++++++++++++++++++++++++++++++++++"
            for key in decoded_json.keys():
                print "%s --> %s" % ( key, decoded_json[key])
            print "++++++++++++++++++++++++++++++++++++++++"
            #self.timer.cancel()
            #exit(8)
        #for key in sorted(decoded_json["user"].keys()):
            #print "%s --> %s" % (key, decoded_json["user"][key])
        
        #print ""
        return True
    def on_error(self, status):
        print status
    
    def printTweetCountAndReset(self):
        self.timer = threading.Timer(self.period, self.printTweetCountAndReset)
        self.timer.start()
        print self.tweets_per_period
        self.tweets_per_period = 0

if __name__ == "__main__":
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    #trends1 = api.trends_place(1)      # Worldwide
    trends1 = api.trends_place(2450022)    # US
    trends = trends1[0]['trends']
    print trends

    for trend in trends:
        print trend["name"]
    
    stream = Stream(auth, l)
    stream.filter(languages=["en"], track=[trend["name"] for trend in trends][:25])
    #stream.filter(languages=["en"], track=list(string.printable))
    
    
