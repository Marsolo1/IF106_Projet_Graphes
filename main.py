from time import time
import pygame as pg
import sys
import random as rd

class World:
	def __init__(self, N:int=0, Sleeping:list=[], Awake:list=[], Edges:list=[], Obstacles:list=[]):
		"""
		Constructor
		"""
		self.N = N
		self.Awake = Awake
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles
		self.Edges = Edges

	def init_world_from_file(self, filename):
		"""
		Load a file and init the world based on that file
		"""
		f = open(filename, 'r')
		for line in f:
			l = line.strip().split(" : ")
			x = l[1].split(",")[0][1:]
			y = l[1].split(",")[1][:-1]
			if l[0] == 'R':
				self.Awake.append(Robot(int(x), int(y)))
			elif l[0].isnumeric():
				self.Sleeping.append(Robot(int(x), int(y)))
			elif l[0] == 'E':
				robotA = self.Awake[0] if x == 'R' else self.Sleeping[int(x)-1]
				robotB = self.Awake[0] if y == 'R' else self.Sleeping[int(y)-1]
				robotA.neighbors.append(robotB)
				robotB.neighbors.append(robotA)
				self.Edges.append((robotA, robotB))
		f.close()
		self.N = max([self.Awake[0].x, self.Awake[0].y] + [r.x for r in self.Sleeping] + [r.y for r in self.Sleeping]) + 1

	def update(self, screen: pg.Surface, psize: int):
		"""
		Update the robots' position and color
		"""
		screen.fill(pg.Color("lightgray"))
		for r in self.Awake:
			pg.draw.circle(screen, pg.Color('red'), (r.x*psize, r.y*psize), psize//2)
			if len(r.targets) > 0:
				r_t = closestRobotInTargets(r, self)
				pg.draw.line(screen, pg.Color("black"), (r.x*psize, r.y*psize), (r_t.x*psize, r_t.y*psize), width=2)


		for r in self.Sleeping:
			pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)
		for r in self.Awake:
			pg.draw.circle(screen, pg.Color('red'), (r.x*psize, r.y*psize), psize//2)
		#not used
		# for t in self.Edges:
		# 	pg.draw.line(screen, pg.Color('green'), (t[0].x*psize, t[0].y*psize), (t[1].x*psize, t[1].y*psize))
	
	def init_target(self):
		"""
		Init the target array at the start of the algorithm
		"""
		for r in self.Awake:
			for rs in self.Sleeping:
				r.targets.append(rs)

	def get_tot_dist(self):
		"""
		Compute the total distance traveled by all the robots awake
		"""
		tot = 0
		for i in range (len(self.Awake)):
			tot += self.Awake[i].distance
		return tot

	def random_generation(self, seed, N, K):
		"""
		Generate a random world based on its size N and a number of robot K
		"""
		self.N = N
		self.Awake = []
		self.Sleeping = []
		rd.seed(seed)
		(m_x, m_y) = rd.randint(0, N-1), rd.randint(0, N-1)
		self.Awake.append(Robot(m_x, m_y))
		for i in range(K):
			rd_nb_x, rd_nb_y = m_x, m_y
			while (m_x == rd_nb_x and m_y == rd_nb_y):
				rd_nb_x, rd_nb_y = rd.randint(0, N-1), rd.randint(0, N-1)
			self.Sleeping.append(Robot(rd_nb_x, rd_nb_y))
		
			

class Robot:
	def __init__(self, x: int, y: int, targets:list=[], neighbors:list=[]):
		"""
		Constructor
		"""
		self.x = x
		self.y = y
		self.targets = targets
		self.distance = 0
		self.neighbors = neighbors
	
	def inc_distance(self):
		"""
		Increase the distance traveled by the robot
		"""
		self.distance += 1
		


def TowardAwakeRobot(robotA: Robot, robotS: Robot):
	"""
	Move robotA toward robotS
	"""
	diff_x = robotA.x - robotS.x
	diff_y = robotA.y - robotS.y

	if abs(diff_x) > abs(diff_y):
		if diff_x > 0:
			robotA.x -= 1
		if diff_x < 0:
			robotA.x += 1
	else:
		if diff_y > 0:
			robotA.y -= 1
		if diff_y < 0:
			robotA.y += 1


def closestRobot(world: World, robotA: Robot) -> Robot:
	"""
	Look for the closest robot
	"""
	n = world.N
	x_max, y_max = n, n
	r = None
	for robot in world.Sleeping:
		diff_x = abs(robot.x - robotA.x)
		diff_y = abs(robot.y - robotA.y)
		if (x_max + y_max > diff_x + diff_y):
			x_max, y_max = diff_x, diff_y
			r = robot
	return r

def closestRobotInTargets(robotA: Robot, world: World) -> Robot:
	"""
	Look for the closest robot in the targets param of the robotA
	"""
	n = world.N
	x_max, y_max = n, n
	r = None
	for robot in robotA.targets:
		diff_x = abs(robot.x - robotA.x)
		diff_y = abs(robot.y - robotA.y)
		if (x_max + y_max > diff_x + diff_y):
			x_max, y_max = diff_x, diff_y
			r = robot
	return r


def compute_sub_list(robota: Robot, robotb: Robot, target: Robot) -> list:
	"""
	Generate two lists of targets by separating the robots
	above and below a line. The line traced is between robota and target
	the lists of targets are then associated to robota and robotb
	"""
	def compute_coef(robota, robotb):
		"""
		Compute the coeffcients for the line between robota and robotb
		"""
		def compute_affine(xa, xb, ya, yb):
			a = (yb-ya)/(xb-xa)
			b = ya-a*xa
			return [a, b]
		return compute_affine(robota.x, robotb.x, robota.y, robotb.y)

	def separate(T, a, b):
		"""
		Separate all the robots in T based on their position compared to the line ax + b
		"""
		T1 = []
		T2 = []
		for i in range(len(T)):
			if T[i].y >= a*T[i].x+b:
				T1.append(T[i])
			else:
				T2.append(T[i])
		return (T1,T2)

	T=robota.targets
	if robota.x != target.x:
		(a, b) = compute_coef(robota, target)
		(T1, T2) = separate(T,a,b)
		robota.targets=T1
		robotb.targets=T2
	else :
		robota.targets=[]
		robotb.targets=[]
		for i in range(len(T)):
			if T[i].x > robota.x:
				robota.targets.append(T[i])
			else:
				robotb.targets.append(T[i])

def are_at_same_place(robota: Robot, robotb: Robot) -> bool:
	"""
	Return whether the robot are at the same place
	"""
	return (robota.x == robotb.x and robota.y == robotb.y)

def wakeUp(world: World, robot: Robot):
	"""
	Wake up a robot
	"""
	world.Sleeping.remove(robot)
	world.Awake.append(robot)

def remove_from_targets(w,rs):
	"""
	Remove a robot rs from all the targets of all awake robots
	"""
	for r in w.Awake:
		if len(r.targets) == 0:
			continue
		for r_t in r.targets:
			if r_t == rs:
				r.targets.remove(rs)
				continue

def awake_robot(w, idx_a, rs):
	"""
	Wake up a robot and compute the targets for the newly awoken robot
	"""
	w.Sleeping.remove(rs)
	w.Awake.append(rs)
	remove_from_targets(w, rs)
	actual = w.Awake[-1]
	if (len (w.Awake[idx_a].targets) > 0):
		compute_sub_list(w.Awake[idx_a], actual, closestRobotInTargets(w.Awake[idx_a], w))


def stupidTravellingSalesman(world: World, screen: pg.Surface, psize: int):
	"""
	Travelling Salesman algorithm (with only one robot moving)
	"""
	N = world.N
	main = world.Awake[0]
	target = closestRobot(world, main)
	iteration = 0
	while len(world.Sleeping) > 0:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				return
		if main.x == target.x and main.y == target.y:
			wakeUp(world, target)
			target = closestRobot(world, main)
		if target is None or main is None:
			continue
		iteration += 1
		print(iteration)
		main.inc_distance()
		TowardAwakeRobot(main, target)
		world.update(screen, psize)
		pg.draw.line(screen, pg.Color("black"), (main.x*psize, main.y*psize), (target.x*psize, target.y*psize), width=2)
		pg.display.flip()
		pg.time.delay(100)

def separateLineAlgo(w: World, screen: pg.Surface, psize: int):
	"""
	Separate the world in districts in order to efficiently awake all robots
	"""
	w.init_target()
	screen.fill(pg.Color('black'))
	iterations = 0
	while len(w.Sleeping) > 0:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				return
		for i in range(len(w.Awake)):
			screen.fill(pg.Color('black'))
			if len(w.Awake[i].targets)!=0:
				closeRT = closestRobotInTargets(w.Awake[i], w)
				if are_at_same_place(w.Awake[i],closeRT) :
					awake_robot(w, i, closeRT)
						
				else:
					TowardAwakeRobot(w.Awake[i], closeRT)
					w.Awake[i].inc_distance()

		iterations+=1
		w.update(screen, psize)
		pg.display.flip()
		pg.time.delay(100)

def screenInit(world, psize):
	"""
	Initialize the screen
	"""
	pg.init()
	screen = pg.display.set_mode((world.N*psize, world.N*psize))
	pg.display.set_caption('Robots')
	screen.fill(pg.Color('lightgray'))
	[pg.draw.circle(screen, pg.Color('red'), (psize*robot.x,
					psize*robot.y), psize//2) for robot in world.Awake]
	[pg.draw.circle(screen, pg.Color('blue'), (psize*robot.x,
					psize*robot.y), psize//2) for robot in world.Sleeping]
	return screen

def save_data_in_file(times, dist):
	"""
	Save performances measurements in a file
	"""
	file = open("data.txt", 'w')
	file.write("times" + "\t" + "distances" + "\n")
	for i in range (len(times)):
		file.write(str(times[i]) + "\t" + str(dist[i]) + "\n")
	file.close()

def measure_perf(N, K, algo):
	"""
	Compute 10 times the algorithms with a world of size NxN and K robots
	"""
	times = []
	dist = []
	for i in range (10):
		w.random_generation(i, N, K)
		c = pg.time.Clock()
		screen = screenInit(w, psize)
		c.tick()
		algo(w, screen, psize)
		c.tick()
		times.append(c.get_time())
		dist.append(w.get_tot_dist())
	save_data_in_file(times, dist)

if __name__ == "__main__":
	N = 60
	psize = 4 # change to 1 in order to optimize the execution time
	w = World()
	w.init_world_from_file(sys.argv[2])
	algos = {"stupid": stupidTravellingSalesman, "lines": separateLineAlgo}
	# measure_perf(100, 100, algos[sys.argv[1]])
	algos[sys.argv[1]](w, pg.display.set_mode((w.N*psize, w.N*psize)), psize)
	pg.quit()
	quit()