import math
from decimal import * #to handle the floating point numbers

class mapping:
	
	'''
	Input num: number of sqaures needed in one row
	Intial mapping to be done so that the calculations are done only once
	int_size : Interval size for sqaures on the graph (forming a cluster)
	precision_val : calculated for
	'''
	def __init__(self,x1,y1,x2,y2,num):
		self.int_size = Decimal(math.fabs(x1-x2))/Decimal(num) #interval size, size of one side of the smallest square
		self.precision_val = int(abs(math.log10(self.int_size))) + 4 #since max would be 3 digits (or hundreds), adding 3 + 1 (adding one more decimals after mantissa for midpoint)
		getcontext().prec = self.precision_val  #setting the number of decimals to handle the loose floating point
		self.midpoint = Decimal(self.int_size/2) #setting the midpoint of the smallest sqaure to be mapped onto the map
		self.x1 = x1 #initial x1
		self.y1 = y1 #initial y1
		self.x2 = x2 #initial x2
		self.y2 = y2 #initial y2

	
	'''
	given a set of x,y points on the map, it returns the co-ordinates which needs to mapped onto the final UI.
	'''
	def map(self,x,y):
		'''
		x - x1 gives the distance of the point from the orginal point
		x - x1 modulus interval_size gives us the distance of the point from the leftmost edge within the shortest sqaure (absolute value)
		x - ((x - x1) mod interval_size) gives the co-ordinate of the point leftmost edge of individual sqaure from the starting point (relative value)
		Then adding the midpoint to move the point from the leftmost edge to the midpoint of the square
		'''
		x_pos = Decimal(x) - ((Decimal(x) - Decimal(self.x1))%Decimal(self.int_size))
		#midpoint addition and checking the boundary condition if point == x2
		x_pos =  Decimal(x_pos) + self.midpoint if x_pos < self.x2 else Decimal(x_pos) - self.midpoint
		
		y_pos = Decimal(y) - ((Decimal(y) - Decimal(self.y1))%Decimal(self.int_size))
		y_pos =  Decimal(y_pos) + self.midpoint if y_pos < self.y2 else Decimal(y_pos) - self.midpoint
		
		return (x_pos,y_pos)

if __name__ == '__main__':
	#test cases
	obj = mapping(-122.75,36.8,-121.75,37.9,1000)
	print obj.map(-122.7489999,36.8)
	print obj.map(-122.749,36.8)
	print obj.map(-122.70,36.9)
	print obj.map(-121.7502,37.9)
