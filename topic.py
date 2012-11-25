import nltk,re
import enchant
from nltk.corpus import brown
from nltk.tag.simplify import simplify_wsj_tag
import operator

class topic():
	
	hashtag = re.compile('#(\w+)')
	url = re.compile('http:[^\s]+')
	discount = re.compile('[0-9|.]+%')
	person = re.compile('@[\w]+')
	d = enchant.Dict("en_US") 
	global_topics = {}
	def readfile(self,filename):
		f = open(filename,'r')
		for line in f:
			tweet = line.split('\t')
			if len(tweet) >= 11:
				print tweet[11]
				self.tag_pos(tweet[11])
		f.close()

	def tag_pos(self,tweet):
		entity = {}
		
		hashtags = self.hashtag.findall(tweet)
		for tag in hashtags:
			entity[tag] = 2 if tag not in entity else entity[tag] + 2
		tweet = self.hashtag.sub('hashtag123 ',tweet)
		
		tweet = self.url.sub('url123 ', tweet)
		
		discounts = self.discount.findall(tweet)
		for discount in discounts:
			entity[discount] = 1 if discount not in entity else entity[discount] + 1
		tweet = self.discount.sub('discount123 ',tweet)
		
		tweet = self.person.sub('person123 ',tweet)
		
		text = nltk.wordpunct_tokenize(tweet)
		tokens = nltk.pos_tag(text)
		simplified_tokens = [(word, simplify_wsj_tag(tag)) for word, tag in tokens]
		
		topic = ""
		
		for i in range(0,len(simplified_tokens)):
			if simplified_tokens[i][0].lower() == 'sale':
				j = i-1
				found = False
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
		#print entity
		if len(entity) > 0:
			topic = entity[0][0]
			if (len(topic.split(" "))>3):
				for i in range(1,len(entity)):
					if len(entity[i][0].split(" "))<3:
						topic = entity[i][0]
			if topic not in self.global_topics:
				self.global_topics[topic] = 1
			return topic
 
 

if __name__ == '__main__':
	#nltk.download()
	obj = topic()
	obj.readfile('searchTweet.data')