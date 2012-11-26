from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import datetime,json,re,time
import enchant
from nltk import wordpunct_tokenize

#from multiprocessing import Pool
import ConfigParser

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

if __name__ == '__main__':
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	tweets = api.search(q='deals OR deal OR sales OR sale',lang='en',result_type='recent',geocode='37.781157,-122.398720,50mi',rpp='100',include_entities='true')
	f = open('searchTweet.data','a+')
	for tweet in tweets:
		#print dir(tweet)
		f.write(str(tweet.created_at) + "\t")
		f.write(str(tweet.entities) + "\t")
		f.write(str(tweet.from_user) + "\t")
		f.write(tweet.from_user_id_str + "\t")
		f.write(tweet.from_user_name.encode('utf-8') + "\t")
		f.write(str(tweet.geo) + "\t")
		f.write(tweet.id_str + "\t")
		f.write(str(tweet.iso_language_code) + "\t")
		#f.write(str(tweet.location) + "\t")
		f.write(str(tweet.metadata) + "\t")
		f.write(str(tweet.parse) + "\t")
		f.write(str(tweet.parse_list) + "\t")
		f.write(str(tweet.profile_image_url) + "\t")
		f.write(str(tweet.profile_image_url_https) + "\t")
		f.write(tweet.source.encode('utf-8') + "\t")
		f.write(tweet.text.encode('utf-8') + "\t")
		f.write(str(tweet.to_user) + "\t")
		f.write(str(tweet.to_user_id_str) + "\t")
		if (tweet.to_user_name):
			f.write(tweet.to_user_name.encode('utf-8') + "\t")
		f.write("\n")
	f.close()
	