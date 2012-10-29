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
consumer_key=config.get('Credentials','consumer_key')
consumer_secret=config.get('Credentials','consumer_secret')

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=config.get('Credentials','access_token')
access_token_secret=config.get('Credentials','access_token')


class StdOutListener(StreamListener):
	""" A listener handles tweets are the received from the stream. 
	This is a basic listener that just prints received tweets to stdout.
"""
	i = 1
	j = 1
	#time = datetime.datetime.now()
	fileObj = None
	#pool = Pool(processes=5) 
	#currTime = -1
	pattern = re.compile('\$+\.*[0-9]+|\$+')
	engCheck = enchant.Dict("en_US")
	def on_data(self, data):
		#print data
		#self.fileObj.write(data)
		result = self.analyzedata(data)
		print 'sent the data'
		return True

	def on_error(self, status):
		print status

	def init(self):
		self.fileObj = open('streamdata','a+')

	def analyzedata(self,data):
		json_data = json.loads(data)
		tokens = wordpunct_tokenize(json_data['text'])
		for i in range(0,len(tokens)):
			eng = False
			token = tokens[i].lower()
			if token == 'deal' or token == 'sale' or token =='deals' or token =='sales' or self.pattern.match(token):
				if i > 0:
					eng = engCheck.check(tokens[i-1].lower())
				elif i < len(tokens) - 1:
					if token == 'deal':
						eng = False if token[i+1].lower() == 'with' else True
					else:
						eng = engCheck.check(tokens[i+1].lower())
				else:
					eng = True
				if eng == True:
					self.fileObj.write(data)
					self.fileObj.flush()
					print 'processed an entry'
					break


if __name__ == '__main__':
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	l.init()
	stream = Stream(auth, l)	
	#time1 = datetime.datetime.now()
	#data = stream.sample()
	i = 1
	while (i == 1):
		try:
			data = stream.filter(locations=[-122.75,36.8,-121.75,37.9])
		except e:
			time.sleep(10)
	'''timediff = datetime.datetime.now() - time1
	print timediff.seconds
	print timediff'''
