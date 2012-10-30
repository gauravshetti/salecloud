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

class StdOutListener(StreamListener):
	""" A listener handles tweets are the received from the stream."""
	fileObj = None						#object for writing into files
	engCheck = enchant.Dict("en_US")	#object for handling english tweets
	#spanCheck = enchant.Dict("es_ES")	#object for handling spanish tweets
	
	pattern = re.compile('\$+\.*[0-9]+|\$+') #regex for checking $ expression followed by digits or $$$$.. 

	def on_data(self, data):
		#print data
		result = self.analyzedata(data)
		print 'sent the data'			#status to know that a tweet was read
		return True

	def on_error(self, status):
		print status					#need more error handling to be done in future

	def init(self):
		self.fileObj = open('twitter.data','a+')	#initializing the object

	def analyzedata(self,data):
		json_data = json.loads(data)			
		tokens = wordpunct_tokenize(json_data['text'])
		for i in range(0,len(tokens)):
			posTweet = False			#flag for identifying a match
			token = tokens[i].lower()
			
			if token == 'deal':
				if i < len(token) - 1:
					posTweet = False if token[i+1] == 'with' else True
			elif self.pattern.match(token):
				posTweet = True
			elif token =='sale' or token =='deals' or token =='sales' or token == 'offer' or token == 'offers':
				if i > 0:
					posTweet = self.engCheck.check(tokens[i-1].lower())
				elif i < len(tokens) - 1:
					posTweet = self.engCheck.check(tokens[i+1].lower())
				else:
					posTweet = True
			elif token=='negociar' or token =='ofertas' or token == 'venta' or token  == 'ofrecer' or token == 'ofrece': #spanish keywords, more test cases to be handled
				'''if i > 0:
					posTweet = self.spanCheck.check(tokens[i-1].lower())
				elif i < len(tokens) - 1:
					posTweet = self.spanCheck.check(tokens[i+1].lower())
				else:'''
				posTweet = True
			
			if posTweet == True:
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
	while (True):
		try:
			data = stream.filter(locations=[-122.75,36.8,-121.75,37.9])
		except e:
			time.sleep(10)
