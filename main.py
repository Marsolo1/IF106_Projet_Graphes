import pygame as pg
import sys
import random as rd

class World:
	def __init__(self, N:int=0, Sleeping:list=[], Awake:list=[], Edges:list=[], Obstacles:list=[]):
		self.N = N
		self.Awake = Awake
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles
		self.Edges = Edges

	def init_world_from_file(self, filename):
		f = open(filename, 'r')
		for line in f:
			l = line.strip().split(" : ")
			x = l[1].split(",")[0][1:]
			y = l[1].split(",")[1][:-1]
			#We suppose that there are only robots and no obstacles
			if l[0] == 'R':
				self.Awake.append(Robot(int(x), int(y)))
			elif l[0].isnumeric():
				self.Sleeping.append(Robot(int(x), int(y)))
			elif l[0] == 'E':
				self.Edges.append((
					self.Awake[0] if x == 'R' else self.Sleeping[int(x)-1],
					self.Awake[0] if y == 'R' else self.Sleeping[int(y)-1]
				))
		f.close()
		self.N = max([self.Awake[0].x, self.Awake[0].y] + [r.x for r in self.Sleeping] + [r.y for r in self.Sleeping]) + 1

	def update(self, screen: pg.Surface, psize: int):
		screen.fill(pg.Color("lightgray"))
		for r in self.Awake:
			pg.draw.circle(screen, pg.Color('red'), (r.x*psize, r.y*psize), psize//2)
			if len(r.targets) > 0:
				r_t = closestRobotInTargets(r, self)
				pg.draw.line(screen, pg.Color("black"), (r.x*psize, r.y*psize), (r_t.x*psize, r_t.y*psize), width=2)


		for r in self.Sleeping:
			pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)
	
	def init_target(self):
		for r in self.Awake:
			for rs in self.Sleeping:
				r.targets.append(rs)

	def get_tot_dist(self):
		tot = 0
		for i in range (len(self.Awake)):
			tot += self.Awake[i].distance
		return tot

	def random_generation(self, seed, N, K):
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
	def __init__(self, x: int, y: int, targets:list=[]):
		self.x = x
		self.y = y
		self.targets = targets
		self.distance = 0
	
	def inc_distance(self):
		self.distance += 1


def TowardAwakeRobot(robotA: Robot, robotS: Robot):
	"""Move robotA toward robotS"""
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
	"""Look for the closest robot"""
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
	"""Look for the closest robot"""
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
	def compute_coef(robota, robotb):
		def compute_affine(xa, xb, ya, yb):
			a = (yb-ya)/(xb-xa)
			b = ya-a*xa
			return [a, b]
		return compute_affine(robota.x, robotb.x, robota.y, robotb.y)

	def separate(T, a, b):
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
	return (robota.x == robotb.x and robota.y == robotb.y)

def wakeUp(world: World, robot: Robot):
	robot.wakeUp()
	world.Sleeping.remove(robot)
	world.Awake.append(robot)

def remove_from_targets(w,rs):
	for r in w.Awake:
		if len(r.targets) == 0:
			continue
		for r_t in r.targets:
			if r_t == rs:
				r.targets.remove(rs)
				continue

def awake_robot(w, idx_a, rs):
	w.Sleeping.remove(rs)
	w.Awake.append(rs)
	remove_from_targets(w, rs)
	actual = w.Awake[-1]
	if (len (w.Awake[idx_a].targets) > 0):
		compute_sub_list(w.Awake[idx_a], actual, closestRobotInTargets(w.Awake[idx_a], w))


def stupidTravellingSalesman(world: World, screen: pg.Surface, psize: int):
	N = world.N
	main = world.Awake[0]
	target = closestRobot(world, main)
	while len(world.Sleeping) > 0:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				return
		if main.x == target.x and main.y == target.y:
			target.wakeUp()
			wakeUp(world, target)
			target = closestRobot(world, main)
		TowardAwakeRobot(main, target)
		world.update(screen, psize)
		pg.draw.line(screen, pg.Color("black"), (main.x*psize, main.y*psize), (target.x*psize, target.y*psize), width=2)
		pg.display.flip()
		pg.time.delay(100)

def travellingSalesman(world: World, screen: pg.Surface, psize: int):
	N = world.N
	main = world.Awake[0]
	target = closestRobot(world, main)
	while len(world.Sleeping) > 0:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				return
		if main.x == target.x and main.y == target.y:
			target.wakeUp()
			wakeUp(world, target)
			target = closestRobot(world, main)
		TowardAwakeRobot(main, target)
		world.update(screen, psize)
		pg.draw.line(screen, pg.Color("black"), (main.x*psize, main.y*psize), (target.x*psize, target.y*psize), width=2)
		pg.display.flip()
		pg.time.delay(100)

def separateLineAlgo(w: World, screen: pg.Surface, psize: int):
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
					new_closeRT = closestRobotInTargets(w.Awake[i], w)
					TowardAwakeRobot(w.Awake[i], new_closeRT)
					w.Awake[i].inc_distance()

		iterations+=1
		w.update(screen, psize)
		pg.display.flip()

def screenInit(world, psize):
	"""Initialize the screen"""
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
	file = open("data.txt", 'w')
	file.write("times" + "\t" + "distances" + "\n")
	for i in range (len(times)):
		file.write(str(times[i]) + "\t" + str(dist[i]) + "\n")
	file.close()

if __name__ == "__main__":
	N = 1000
	psize = 1
	w = World()
	#w.init_world_from_file(sys.argv[1])
	times = []
	dist = []
	c = pg.time.Clock()
	for i in range (10):
		w.random_generation(i, N, 10)
		screen = screenInit(w, psize)
		# stupidTravellingSalesman(w, screen, psize)
		w.init_target()
		c.tick()
		separateLineAlgo(w, screen, psize)
		c.tick()
		times.append(c.get_time())
		dist.append(w.get_tot_dist())
	save_data_in_file(times, dist)

	pg.quit()
	quit()