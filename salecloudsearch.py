from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import datetime,json,re,time,sched
import enchant
from nltk import wordpunct_tokenize

#from multiprocessing import Pool
import ConfigParser
import MySQLdb

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
sinceID = 0

def new_timed_call(calls_per_second, callback, *args, **kw):
	period = 1.0 / calls_per_second
	def reload():
		callback(*args, **kw)
		scheduler.enter(period, 0, reload, ())
	scheduler.enter(period, 0, reload, ())

def searchTweets():
	global sinceID
	tweetslist = api.search(q='#sale OR #discount OR #deal OR #deals OR #offer OR (deals -"deals with") OR (deal -"big deal"-"deal with" -"deal wit" -"deal wid" -"deal w/" -"deal of" -"deal between" -"deal to" -"kind of deal" -"done deal" -"cant deal") OR (sales -force -man -woman -men -women) OR sale OR discount OR "special offer" OR "special offers"',lang='en',result_type='recent',geocode='37.781157,-122.398720,50mi',rpp='100',include_entities='true',since_id=sinceID)
	#tweetslist = api.search(q='giants',result_type='recent',since_id=sinceID)
	tweets = tweetslist['statuses']
	#f = open('searchTweet2.data','a+')
	#print len(tweets)
	db=MySQLdb.connect(user="root", passwd="",db="salecloud")
	c=db.cursor()
	c.execute("""SELECT tweetid FROM tweets WHERE tweetid = 274960883455774720""")
	rows = c.fetchall()
	print rows
	#print rows[0]
	for tweet in tweets:
		print tweet['id']
		#print tweet['created_at']
		#print tweet['text']
		if tweet.get('retweeted_status'):
			tweetid = tweet['retweeted_status']['id']
			c.execute("""SELECT * FROM tweets WHERE tweetid = %s""",tweetid)
			rows = c.fetchall()
			if rows:
				new_retweetcount = rows[0][5] + 1
				new_totalfollowers = rows[0][9] + tweet['user']['followers_count']
				new_numtweets = rows[0][10] + 1
				c.execute("""UPDATE tweets SET retweet_count = %s, total_followers = %s, num_tweets = %s WHERE tweetid = %s""",(new_retweetcount, new_totalfollowers, new_numtweets, tweetid))
				break
			else:
				continue	
		else:
			tweetid = tweet['id']
		url = 	''
		if tweet['entities']['urls']:
			url = tweet['entities']['urls'][0]['url'].encode('utf-8')
		hastags = []
		hashtagtxt = ''
		if tweet['entities']['hashtags']:
			hastags = tweet['entities']['hashtags']
			for hashtag in hastags:
				hashtagtxt += hashtag['text']
				hashtagtxt += '|'
		try:
			c.execute("""INSERT INTO tweets (tweetid, tweet_date, tweet_text, screen_name,total_followers,urls,hashtag,num_tweets) values(%s,%s,%s,%s,%s,%s,%s,1) """,(tweetid,tweet['created_at'].encode('utf-8'),tweet['text'].encode('utf-8'),tweet['user']['screen_name'].encode('utf-8'),tweet['user']['followers_count'],url,hashtagtxt))
		except:
			print "DB exception found"
			pass
		print "since id"
		print tweetslist['search_metadata']['max_id']
		sinceID = tweetslist['search_metadata']['max_id']
		
if __name__ == '__main__':
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	
	scheduler = sched.scheduler(time.time, time.sleep)

	new_timed_call(0.083,searchTweets)   
	scheduler.run()	
