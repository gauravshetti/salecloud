import nltk,re
from nltk.corpus import brown
from nltk.tag.simplify import simplify_wsj_tag
from nltk import corpus
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
	loc_topic_at = re.compile(' at @([\w]+)')
	loc_topic_at2 = re.compile(' (sales|sale|deal|deals) @([\w]+)')
	global_topics = {}					#global dict for maintaing entities database
	global_topics_not = {}
	
	def __init__(self):
		self.read_from_topics()

	def create_connection(self):
		con = mdb.connect('localhost', 'root', '', 'salecloud')
		return con

	def close_connection(self,con):
		con.close()


	def update_db(self,con):
		cur = con.cursor()
		cur.execute("SELECT tweet_text,tweetid FROM tweets WHERE processed=0")
		rows = cur.fetchall()
		cur.close()

		if len(rows) > 0:
			cur = con.cursor()
			for row in rows:
				topic = self.tag_pos(row[0].lower())
				print row[1]
				print row[0]
				print topic
				if topic != None:
					cur.execute("UPDATE tweets SET entity= %s ,processed = %s WHERE tweetid= %s", (topic , '1', str(row[1])))
			cur.close()
			self.write_into_topics()

	def tag_pos(self,tweet):
		entity = {}					#entity for the current tweet
		
		if (self.loc_topic_at.search(tweet)):
			topic = self.loc_topic_at.search(tweet).group(1)
			return topic
		if (self.loc_topic_at2.search(tweet)):
			topic = self.loc_topic_at2.search(tweet).group(2)
			return topic

		#weigh the hashtags, WEIGHTAGE = 2. And replace it with hastag123
		hashtags = self.hashtag.findall(tweet)
		for tag in hashtags:
			entity[tag] = 6 if tag not in entity else entity[tag] + 6
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
			if simplified_tokens[i][0].lower() == 'sale' or simplified_tokens[i][0].lower() == 'sales' or simplified_tokens[i][0].lower() == 'deal' or simplified_tokens[i][0].lower() == 'deals':
				j = i-1
				found = False
				#going backwards
				while (j >= 0 and not(found)):
					if (simplified_tokens[j][1]=='NP' or simplified_tokens[j][1]=='N') and simplified_tokens[j][0].lower() not in ('url123','hashtag123','discount123','person123','rt'):
						word = simplified_tokens[j][0].lower()
						if  j-1 >= 0:
							scan = True
							while j >= 0 and (scan):
								if (simplified_tokens[j-1][1] == 'NP' or simplified_tokens[j-1][1] == 'N' or simplified_tokens[j-1][1] == 'NUM' or simplified_tokens[j-1][0] == "'" or simplified_tokens[j-1][0] == "-") and simplified_tokens[j-1][0].lower() not in ('url123','hashtag123','discount123','person123','rt'):
									word = simplified_tokens[j-1][0].lower() + " " + word
									j = j-1
								else:
									scan = False
						if word!="":
							entity[word] = 4 if word not in entity else entity[word] + 4
							found = True
					j = j-1
			
			if simplified_tokens[i][0].lower() == 'off' or simplified_tokens[i][0].lower() == 'on' or simplified_tokens[i][0].lower() == 'at' or simplified_tokens[i][0].lower() == 'with' or simplified_tokens[i][0].lower() == 'deal':
				if simplified_tokens[i][0].lower() == 'at':
					weightage = 6
				else:
					weightage = 3
				j=i+1
				found = False
				#forward look-up
				word =""
				while(j < len(simplified_tokens) and not(found)):
					if (simplified_tokens[j][1]=='NP' or simplified_tokens[j][1]=='N' ) and simplified_tokens[j][0].lower() not in ('url123','hashtag123','discount123','person123','on','rt','sale','.'):
						word = simplified_tokens[j][0].lower()
						j = j + 1
						if  j < len(simplified_tokens):
							scan = True
							while j < len(simplified_tokens) and (scan) :
								if (simplified_tokens[j][1] == 'NP' or  simplified_tokens[j][1] == 'N' or  simplified_tokens[j][1] == 'NUM' or simplified_tokens[j][0] == "-" or simplified_tokens[j][0] == ".") and simplified_tokens[j][0].lower() not in ('url123','hashtag123','discount123','person123','rt','sale') :
									if simplified_tokens[j][1] == '.':
										if len(simplified_tokens[j-1][0])==1 and j+1<len(simplified_tokens):
											word = word + "." +simplified_tokens[j+1][0]
											scan = False
										break
									word = word + " " + simplified_tokens[j][0].lower()
									j = j + 1
								else:
									if word == "":
										j=j+1
									else:
										scan = False
						if word!="":
							entity[word] = weightage if word not in entity else entity[word] + weightage
							found = True
					j = j+1
		for key in entity.keys():
			if key in self.global_topics:
				entity[key] = entity[key] + 10
			if key in self.global_topics_not:
				entity[key] = 0
		entity = sorted(entity.iteritems(), key=operator.itemgetter(1), reverse=True)
		
		for i in range(0,len(entity)):
			topic = entity[i][0]
			if topic not in self.global_topics_not:
				if (len(topic.split(" "))>3):
					words = topic.split(" ")
					if words[len(words)-2] == "'":
						topic = words[len(words)-3] + " " + words[len(words)-2] + words[len(words)-1]
					elif words[len(words)-1] == "'":
						topic = words[len(words)-3] + " " + words[len(words)-2]
					else:
						topic = words[len(words)-2] + " " + words[len(words)-1]
				elif (len(topic.split(" "))>2):
					words = topic.split(" ")
					for i in range(0,len(words)):
						if i == 0:
							topic = words[i]
						elif words[i-1] == "'":
							topic = topic + words[i]
						elif words[i] == "'":
							topic = topic + words[i]
						else:
							topic = topic + " " +words[i] 
				if topic not in self.global_topics_not:
					if topic not in self.global_topics and topic!='':
						self.global_topics[topic] = 1
					break
		return topic
 
 	def read_from_topics(self):
 		if not(os.path.exists("global_topics")):
 			output = open('global_topics', 'wb')
 			output.close()
 		else:
 			output = open('global_topics', 'r+')
 			lines = output.readlines()
 			for k in lines:
 				self.global_topics[k.rstrip('\n')] = 1
 			output.close()
 		if not(os.path.exists("global_topics_not")):
 			output = open('global_topics_not', 'wb')
 			output.close()
 		else:
 			output = open('global_topics_not', 'r')
 			lines = output.readlines()
 			for k in lines:
 				self.global_topics_not[k.rstrip('\n')] = 1
 			output.close()

 	def write_into_topics(self):
 		output = open('global_topics', 'w')
 		for k in self.global_topics.iterkeys():
 			output.write(k)
 			output.write('\n')
 		output.close()
 		output = open('global_topics_not', 'w')
 		for k in self.global_topics_not.iterkeys():
 			output.write(k)
 			output.write('\n')
 		output.close()

if __name__ == '__main__':
	#nltk.download()
	obj = topic()
	#obj.readfile('searchTweet.data')
	while(True):
		try:
			con = obj.create_connection()
			obj.update_db(con)
			obj.close_connection(con)
			print "\nsleeping for 60 seconds"
			time.sleep(60)
			
		except KeyboardInterrupt:
			print "exiting gracefully"
			sys.exit()