import nltk,re
import enchant
from nltk.corpus import brown
from nltk.tag.simplify import simplify_wsj_tag
import operator, os
import MySQLdb as mdb
import pickle
import time
import sys

class topic():
	
	hashtag = re.compile('#(\w+)') 		#identify hastags
	url = re.compile('http:[^\s]+') 	#identify urls
	discount = re.compile('[0-9|.]+%') 	#identify discounts
	person = re.compile('@[\w]+') 		#person referalls
	d = enchant.Dict("en_US")			#object for identifying english words
	global_topics = {}					#global dict for maintaing entities database
	
	def __init__(self):
		self.read_from_topics()

	def create_connection(self):
		con = mdb.connect('localhost', 'root', '', 'salecloud')
		return con

	def close_connection(self,con):
		con.close()

	def update_db(self,con):
		cur = con.cursor()
		cur.execute("SELECT tweet_text,tweetid FROM tweets WHERE processed = 0")
		rows = cur.fetchall()
		cur.close()

		if len(rows) > 0:
			cur = con.cursor()
			for row in rows:
				topic = self.tag_pos(row[0].lower())
				print row[1]
				if topic != None:
					cur.execute("UPDATE tweets SET entity= %s ,processed = %s WHERE tweetid= %s", (topic , '1', str(row[1])))
				else:
					cur.execute("UPDATE tweets SET processed = %s WHERE tweetid= %s", ('1', str(row[1])))
			cur.close()
			self.write_into_topics()

	def tag_pos(self,tweet):
		entity = {}					#entity for the current tweet
		
		#weigh the hashtags, WEIGHTAGE = 2. And replace it with hastag123
		hashtags = self.hashtag.findall(tweet)
		for tag in hashtags:
			entity[tag] = 2 if tag not in entity else entity[tag] + 2
		tweet = self.hashtag.sub('hashtag123 ',tweet)
		
		#replace the urls with url123
		tweet = self.url.sub('url123 ', tweet)
		
		#weigh the discounts, WEIGHTAGE = 1. And replace it with discount123
		discounts = self.discount.findall(tweet)
		for discount in discounts:
			entity[discount] = 1 if discount not in entity else entity[discount] + 1
		tweet = self.discount.sub('discount123 ',tweet)
		
		#replace the mentions by person123
		tweet = self.person.sub('person123 ',tweet)
		
		text = nltk.wordpunct_tokenize(tweet)
		tokens = nltk.pos_tag(text)
		simplified_tokens = [(word, simplify_wsj_tag(tag)) for word, tag in tokens]
		
		topic = ""
		
		for i in range(0,len(simplified_tokens)):
			if simplified_tokens[i][0].lower() == 'sale':
				j = i-1
				found = False
				#going backwards
				while (j > 0 and not(found)):
					if (simplified_tokens[j][1]=='NP' or simplified_tokens[j][1]=='N') and simplified_tokens[j][0].lower() not in ('url123','hashtag123','discount123','person123','rt'):
						word = simplified_tokens[j][0].lower()
						if  j-1 > 0:
							scan = True
							while j > 0 and (scan):
								if (simplified_tokens[j-1][1] == 'NP' or simplified_tokens[j-1][1] == 'N' or simplified_tokens[j-1][1] == 'NUM' or simplified_tokens[j-1][0] == "'" or simplified_tokens[j-1][0] == "-") and simplified_tokens[j-1][0].lower() not in ('url123','hashtag123','discount123','person123','rt'):
									word = simplified_tokens[j-1][0].lower() + " " + word
									j = j-1
								else:
									scan = False
						if word!="":
							entity[word] = 4 if word not in entity else entity[word] + 4
							found = True
					j = j-1
			
			if simplified_tokens[i][0].lower() == 'off' or simplified_tokens[i][0].lower() == 'on' or simplified_tokens[i][0].lower() == 'at':
				j=i+1
				found = False
				#forward look-up
				while(j < len(simplified_tokens) and not(found)):
					if simplified_tokens[j][1]=='NP' and simplified_tokens[j][0].lower() not in ('url123','hashtag123','discount123','person123','on','.','rt'):
						word = simplified_tokens[j][0].lower()
						j = j+1
						if  j < len(simplified_tokens):
							scan = True
							while j < len(simplified_tokens) and (scan) :
								if (simplified_tokens[j][1] == 'NP' or  simplified_tokens[j][1] == 'N' or  simplified_tokens[j][1] == 'NUM' or simplified_tokens[j][0] == "-") and simplified_tokens[j][0].lower() not in ('url123','hashtag123','discount123','person123','.','rt') :
									word = word + " " + simplified_tokens[j][0].lower()
									j = j + 1
								else:
									if word == "":
										j=j+1
									else:
										scan = False
						if word!="":
							entity[word] = 3 if word not in entity else entity[word] + 3
							found = True
					j = j+1
		for key in entity.keys():
			if key in self.global_topics:
				entity[key] = entity[key] + 10
		entity = sorted(entity.iteritems(), key=operator.itemgetter(1), reverse=True)
		
		if len(entity) > 0:
			topic = entity[0][0]
			if (len(topic.split(" "))>3):	#choose a diff topic if current topic is greater than 3 words
				for i in range(1,len(entity)):
					if len(entity[i][0].split(" "))<3:
						topic = entity[i][0]
			if topic not in self.global_topics:
				self.global_topics[topic] = 1
			return topic
 
 	def read_from_topics(self):
 		if not(os.path.exists("global_topics.pkl")):
 			output = open('global_topics.pkl', 'wb')
 			temp = {}
 			pickle.dump(temp,output)
 			output.close()
 		else:
 			pkl_file = open('global_topics.pkl', 'rb')
 			self.global_topics = pickle.load(pkl_file)
 			pkl_file.close()

 	def write_into_topics(self):
 		pkl_file = open('global_topics.pkl', 'wb')
 		pickle.dump(self.global_topics, pkl_file)
 		pkl_file.close()

if __name__ == '__main__':
	#nltk.download()
	obj = topic()
	#obj.readfile('searchTweet.data')
	while(True):
		try:
			con = obj.create_connection()
			obj.update_db(con)
			obj.close_connection(con)
			print "sleeping for 60 seconds"
			time.sleep(60)
			
		except KeyboardInterrupt:
			print "exiting gracefully"
			sys.exit()