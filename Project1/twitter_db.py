#!env python


from __future__ import print_function
import tweepy
import json
from pymongo import MongoClient

import time
import threading

import random

import sys

import logging
#logging.basicConfig(format='%(levelname)s:  %(message)s', level=logging.INFO)
logger = logging.getLogger(__file__)
logging.info("loading %s" % (__file__))

MONGO_HOST= 'mongodb://localhost/twitterdb'  # assuming you have mongoDB installed locally
# and a database called 'twitterdb'


from twitterkey import TwitterKey

ACCESS_TOKEN = TwitterKey.access_token
ACCESS_TOKEN_SECRET = TwitterKey.access_token_secret
CONSUMER_KEY = TwitterKey.consumer_key
CONSUMER_SECRET = TwitterKey.consumer_secret


class StreamListener(tweepy.StreamListener):    
    num_collected = 0
    #This is a class provided by tweepy to access the Twitter Streaming API. 
    def __init__(self, time_limit=10, **kwargs):
        self.start_time = time.time()
        self.limit = time_limit
        super(StreamListener, self).__init__(**kwargs)
 
    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
 
    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False
 
    def on_data(self, data):
        
        if ((time.time() - self.start_time) < self.limit):
            #This is the meat of the script...it connects to your mongoDB and stores the tweet
            try:
                client = MongoClient(MONGO_HOST)
                
                # Use twitterdb database. If it doesn't exist, it will be created.
                db = client.twitterdb
        
                # Decode the JSON from Twitter
                datajson = json.loads(data)
                
                #grab the 'created_at' data from the Tweet to use for display
                created_at = datajson['created_at']
     
                #print out a message to the screen that we have collected a tweet
                print("Tweet collected at " + str(created_at))
                
                #insert the data into the mongoDB into a collection called twitter_search
                #if twitter_search doesn't exist, it will be created.
                db.twitter_search.insert(datajson)
                self.__class__.num_collected += 1
            except Exception as e:
                print(e)
            return True
        else:
            print("Collected %s tweets" % (self.__class__.num_collected,))
            return False

            
def getTopWords(auth, us_only=False):
    api = tweepy.API(auth)
    if us_only:
        trends1 = api.trends_place(2450022)    # US
    else:
        trends1 = api.trends_place(1)      # Worldwide
    return [trend["name"] for trend in trends1[0]['trends']]

def getTopNWords(auth, n=None):
    if n is None:
        return getTopWords(auth)
    else:
        return getTopWords(auth)[:n]

    
def startUpScan(auth, time_to_collect_for, topic_count=None):
    sys.stderr.write("Running scan... %s\n" % (time.time(),))
    
    #Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
    listener = StreamListener(time_to_collect_for, api=tweepy.API(wait_on_rate_limit=True)) 
    streamer = tweepy.Stream(auth=auth, listener=listener)
    
    WORDS = getTopNWords(auth, topic_count)
    print("Tracking: " + str(WORDS))
    streamer.filter(track=WORDS)
    

def runEveryNSeconds(func, loop_time, repeat=None):
    
    if (repeat is not None) and (repeat == 0):
        pass
    else:
    
        repeats_left = None if (repeat is None) else (repeat - 1)
        
        timer = threading.Timer(loop_time, (lambda : runEveryNSeconds(func, loop_time, repeat=repeats_left)))
        timer.start()
    
    # Run func
    func()

    
def runInNSeconds(func, delay_time):
    timer = threading.Timer(delay_time, func)
    timer.start()


def runCollectionLoop(num_days_to_collect=3, collection_loop_minutes=5, period_seconds=60):
    
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    repeat_counts = int((num_days_to_collect * (24*60)) / collection_loop_minutes)
    potential_delays = [ i * period_seconds for i in range(0, int(((collection_loop_minutes * 60) / period_seconds)))]
    
    
    def sampleFunc():
        runInNSeconds( (lambda : startUpScan(auth, period_seconds)), random.choice(potential_delays))
    
    runEveryNSeconds(sampleFunc, (60*collection_loop_minutes), repeat=repeat_counts)
    


if __name__ == "__main__":
    
    runCollectionLoop()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
