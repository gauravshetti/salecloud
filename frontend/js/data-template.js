var map_data = {
	
	'buildtime': 'October 12, 2012 13:14:00',
	'points':[
		{
			'pointid': 1,
			'lat': 37.8084599,
			'long': -122.4142845,
			'color': 'white',
			'opacity': 0.7,
			'size': 50,
			'tweets': [
				{
					'tweetid':1234,
					'screen_name': 'arian',
					'time': 'October 12, 2012 13:14:00',
					'text': 'Some tweet about sales' 		
				},
				{
					'tweetid':1234,
					'screen_name': 'arian2',
					'time': 'October 12, 2012 13:14:00',
					'text': 'tweet2' 		
				},
				{
					'tweetid':1234,
					'screen_name': 'arian3',
					'time': 'October 12, 2012 13:14:00',
					'text': 'tweet3' 		
				}
				
			]//tweets
		},
		{
			'pointid': 2,
			'lat': 37.81,
			'long': -122.42,
			'color': 'white',
			'opacity': 0.7,
			'size': 50,
			'tweets': [
				{
					'tweetid':1234,
					'screen_name': 'arian',
					'time': 'October 12, 2012 13:14:00',
					'text': 'Some tweet about sales' 		
				}
				
			]
		},
		{
			'pointid': 3,
			'lat': 37.79,
			'long': -122.43,
			'color': 'white',
			'opacity': 0.7,
			'size': 50,
			'tweets': [
				{
					'tweetid':1234,
					'screen_name': 'arian',
					'time': 'October 12, 2012 13:14:00',
					'text': 'Some tweet about sales' 		
				}
				
			]
		},
		{
			'pointid': 4,
			'lat': 37.79,
			'long': -122.44,
			'color': 'white',
			'opacity': 0.7,
			'size': 50,
			'tweets': [
				{
					'tweetid':1234,
					'screen_name': 'arian',
					'time': 'October 12, 2012 13:14:00',
					'text': 'Some tweet about sales' 		
				}
				
			]
		},
		{
			'pointid': 5,
			'lat': 37.78,
			'long': -122.44,
			'color': 'white',
			'opacity': 0.7,
			'size': 50,
			'tweets': [
				{
					'tweetid':1234,
					'screen_name': 'arian',
					'time': 'October 12, 2012 13:14:00',
					'text': 'Some tweet about sales' 		
				}
				
			]
		}
	]//points

};

var bubble_data = {
	children:[
		{
			topic:"Topic 1",//this must be unique (used as primary key)
			value: 4,//this is the weight. have to call it "value" for d3 to understand it's a weight
			color:"blue",
			tweets:[
				{tweetid:123, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"},
				{tweetid:124, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"}
			]//tweets
		},
		{
			topic:"Topic 2",
			value: 80,
			color:"green",
			tweets:[
				{tweetid:125, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"},
				{tweetid:126, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"}
			]//tweets
		},
		{
			topic:"Topic 3",
			value: 40,
			color:"red",
			tweets:[
				{tweetid:127, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"},
				{tweetid:128, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"}
			]//tweets
		},
		{
			topic:"Topic 4",
			value: 75,
			color:"orange",
			tweets:[
				{tweetid:129, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"},
				{tweetid:130, screen_name:"arian", time:"October 12, 2012 13:14:00", text:"blah"}
			]//tweets
		}
	]
}