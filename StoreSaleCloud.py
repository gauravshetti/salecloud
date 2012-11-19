from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import datetime,json,re,time
from datetime import date, timedelta
import enchant
from nltk import wordpunct_tokenize
import threading
import os

#from multiprocessing import Pool
import ConfigParser
import re

config = ConfigParser.RawConfigParser()
config.read('twitter.credentials')

# Go to http://dev.twitter.com and create an app. 
# The consumer key and secret will be generated for you after

consumer_key = config.get('Credentials','consumer_key')
consumer_secret = config.get('Credentials','consumer_secret')

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token = config.get('Credentials','access_token')
access_token_secret = config.get('Credentials','access_token_secret')

def isSalerelated(tweettxt):
	tweettxt = tweettxt.encode('utf-8')
	salepattern = 'holiday|guess|free|sale|sales|deal|promotion|discount|great%20price|promotions'
	if re.search(salepattern, str(tweettxt).lower()):
		return True

def isGoodforSale(post):
	if (post.created_at.date() > (datetime.date.today() - timedelta(3))):
		if (isSalerelated(post.text)):
			return True

def getStoreNames(filename):
	sfile = open(filename, 'r')
	storeNames = []
	for line in sfile:
		storeNames.append(line.split(',')[0])
	sfile.close()
	return storeNames

def getSavedTweetsIds(filename):
	idfile = open(filename, 'r')
	ids = []
	for tweetid in idfile:
		ids.append(tweetid[:-1])
	idfile.close()
	return ids

def saveNewTweetId(filename, id):
	idfile = open(filename, 'a')
	idfile.write(id + '\n')
	idfile.close()
					
def saveNewTweet(filename, tweet):
	with open(filename, 'w+') as fp:
		json.dump(tweet, fp)
					
def getTweetDictionary(tweet):
	dictionary = {}
	dictionary["tweetid"] = tweet.id
	dictionary["screen_name"] = tweet.user.screen_name
	dictionary["time"] = str(tweet.created_at) 
	dictionary["text"] = tweet.text
	#jsonTweet = json.dumps(dictionary)
	#jsonTweet = JSONEncoder.encode(dictionary)
	return dictionary
	
def getSavedTweets(filename):
	#savedTweets = []
#	for line in filename:
	tweet = []
	if os.stat(filename)[6]==0:
		return tweet
	
	f = open(filename, 'r')
	filetext = f.read()
	tweet = json.loads(filetext)
	return tweet

def getlat(screenName):
	sfile = open('storedetails.txt', 'r')
	lats = []
	for line in sfile:
		if line.split(',')[0] == '@'+ screenName:
			sfile.close()
			return line.split(',')[1]

def getlong(screenName):
	sfile = open('storedetails.txt', 'r')
	lats = []
	for line in sfile:
		if line.split(',')[0] == '@'+ screenName:
			sfile.close()
			return line.split(',')[2]	


def saveTweetsFormatted(tweetlist):
	dataJson = {}
	dataJson['buildtime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	tweets = []
	for tweet in tweetlist:
		tweetlat = getlat(tweet['screen_name'])
		tweetlong = getlong(tweet['screen_name'])
		points = dataJson.get('points')
		latlongfound = False
		if points:
			for point in points:
				if (tweetlat in point.values()) and (tweetlong in point.values()):
					latlongfound = True
					tweets = point['tweets']
					tweets.append(tweet)
					#point['tweets'] = tweets
			if not latlongfound:
				point = {}
				point['pointid'] = 1
				point['lat'] = tweetlat
				point['long'] = tweetlat
				point['color'] = 'white'
				point['opacity'] = '0.7'
				point['size'] = '50'
				tweets = []
				tweets.append(tweet)
				point['tweets'] = tweets
				points.append(point)
				#dataJson['points'] = points
		else:
			points = []
			point = {}
			point['pointid'] = 1
			point['lat'] = tweetlat
			point['long'] = tweetlong
			point['color'] = 'white'
			point['opacity'] = '0.7'
			point['size'] = '50'
			tweets = []
			tweets.append(tweet)
			point['tweets'] = tweets
			points.append(point)
			dataJson['points'] = points

	with open('output.json', 'w+') as fp:
		json.dump(dataJson, fp, sort_keys=True, indent=4) 
		
if __name__ == '__main__':
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	storedetails_filename = 'storedetails.txt'
	ids_filename = "ids.txt"
	savedTweets_filename = "savedTweets.txt"
	storeNames = getStoreNames (storedetails_filename)
	savedTweetIds = getSavedTweetsIds(ids_filename)
	tweetList = []
	
	for storeName in storeNames:
		storeTimeline = api.user_timeline(screen_name=storeName)
		for tweet in storeTimeline:	
			if isGoodforSale(tweet):
				tweetId = str(tweet.id)
				if not tweetId in savedTweetIds:
					savedTweetIds.append(tweetId)
					saveNewTweetId(ids_filename, tweetId)
					#saveNewTweet(savedTweets_filename, getTweetDictionary(tweet))
					tweetList.append(getTweetDictionary(tweet))
					
	savedtweets = getSavedTweets(savedTweets_filename)
	if savedtweets:
		for savedtweet in savedtweets:
			tweetList.append(savedtweet)
	saveNewTweet(savedTweets_filename,tweetList)	
	saveTweetsFormatted(tweetList)
		
		