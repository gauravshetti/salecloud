import nltk,re
from topic import topic 

class node:
	def __init__(self,tweetid,date,name,userid,text):
		self.text = text
		self.name = name
		self.date = date
		self.tweetid = tweetid
		self.userid = userid
		self.topic = ""

class build:
	wordregex = re.compile('\w+')
	urlregex = re.compile('(//t\.co/)')
	dotregex = re.compile('\.')
	unwntrepregex = re.compile("'|-|/")
	numregex = re.compile('[^0-9|.]+')
	def __init__(self):
		self.tweetlist=[]
		self.searchIndex={}
		self.stopwords = {}
		for word in nltk.corpus.stopwords.words('english'):
			self.stopwords[word]=1
		self.stopwords['@'] = 1
		self.stopwords['rt'] = 1
		self.stopwords['#'] = 1
		self.stopwords['http'] = 1
		self.stopwords['tco'] = 1
		self.stopwords['na'] = 1
		self.stopwords['want'] = 1
		self.stopwords['ta'] = 1
		self.topicobj = topic()

	def buildfromfile(self,filename):
		f = open(filename,'r+')
		for line in f:
			tweet = line.split('\t')
			if len(tweet) >= 11:
				self.build_index_node(tweet)
		f.close() 

	def build_index_node(self,tweet):
		obj = node(tweet[6],tweet[0],tweet[2],tweet[3],tweet[11])
		self.tweetlist.append(obj)			#main storage for tweet
		currentIndex = len(self.tweetlist)	#index of the storage to be stored in indices
		obj.topic = self.topicobj.tag_pos(tweet[11])
		tokens = self.unwntrepregex.sub(' ',tweet[11]).lower()
		tokens = nltk.word_tokenize(tokens)
		for token in tokens:
			subtok = []
			if token not in self.stopwords and (self.wordregex.findall(token)) and not(self.urlregex.match(token)) and len(token)!=1:
				if (self.numregex.match(token)):
					token = self.dotregex.sub('',token)
				else:
					subtok = token.split(".")
				if len(subtok) == 0:
					self.searchIndex[token] = self.searchIndex[token] + ","+str(currentIndex) if token in self.searchIndex else str(currentIndex)
				else:
					for tok in subtok:
						self.searchIndex[tok] = self.searchIndex[tok] + ","+str(currentIndex) if token in self.searchIndex else str(currentIndex)
 

if __name__=='__main__':
	salecloud = build()
	salecloud.buildfromfile('searchTweet.data')
	print salecloud.tweetlist[1].topic



