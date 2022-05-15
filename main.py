import numpy as np
import pygame as pg

class World:
	def __init__(self, N = 0, Sleeping = [], Main = [], Edges = [], Obstacles=None):
		self.N = N
		self.Awake = Main
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles
		self.Edges = Edges
	
	def init_world_from_file (self, filename):
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

	def init_target(self):
		for r in self.Awake:
			for rs in self.Sleeping:
				r.targets.append(rs)

class Robot:
	def __init__(self, x: int, y: int ,targets = []):
		self.x = x
		self.y = y
		self.targets = targets

def TowardAwakeRobot(robotA, robotS):
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
			
def closestRobot(world, robotA):
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

def closestRobot_i(world, robotA):
	"""Look for the closest robot"""
	n = world.N
	x_max, y_max = n, n
	i_max = 0
	for i in range (len(world.Sleeping)):
		diff_x = abs(world.Sleeping[i].x - robotA.x)
		diff_y = abs(world.Sleeping[i].y - robotA.y)
		if (x_max + y_max > diff_x + diff_y):
			x_max, y_max = diff_x, diff_y
			i_max = i
	return i_max

def closestRobotInTargets(robotA, world):
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

def closestRobotInTargets_i(world, robotA):
	"""Look for the closest robot"""
	n = world.N
	x_max, y_max = n, n
	i_max = 0
	for i in range (len(robotA.targets)):
		diff_x = abs(robotA.targets[i].x - robotA.x)
		diff_y = abs(robotA.targets[i].y - robotA.y)
		if (x_max + y_max > diff_x + diff_y):
			x_max, y_max = diff_x, diff_y
			i_max = i
	return i_max

def compute_sub_list(robota,robotb, target):
	def compute_coef(robota,robotb):
		def compute_affine(xa,xb,ya,yb):
			a=(yb-ya)/(xb-xa)
			b=ya-a*xa
			return (a,b)
		return compute_affine(robota.x,robotb.x,robota.y,robotb.y)
	def separate(T,a,b):
		T1=[]
		T2=[]
		for i in range(len(T)):
			if T[i].y >= a*T[i].x+b:
				T1.append(T[i])
			else :
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
	print(robotb.targets)

def are_at_same_place(robota,robotb):
	return (robota.x==robotb.x and robota.y==robotb.y)

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
	# print(len(w.Sleeping))
	# if len(actual.targets) > 0:
	# 	idx = w.Sleeping.index(closestRobotInTargets(actual, w))
	# 	print(w.Sleeping[idx].targets)

	# 	compute_sub_list(actual, w.Sleeping[idx])
	# 	print(w.Sleeping[idx].targets)

		# print("Actual")
		# print(actual.targets)
		# print("DEst")

		# print(w.Sleeping[idx].targets)



def test_execution():
	N = 20
	Sleeping = [Robot(x, y, targets) for (x,y,targets) in [[0, 5, []], [5, 6, []], [12, 7, []]]]
	S = len(Sleeping)
	Main = Robot( N//2, N//2, Sleeping)
	Awaken = [Main]
	w = World(N, Awaken[0], Sleeping)
	iterations = 0
	while len(Awaken)<=S:
		if iterations == 0 :
			compute_sub_list(Awaken[0],closestRobot(w, Awaken[0]))
			print(Awaken[0].targets)
			print(closestRobot(w, Awaken[0]))
		for i in range(len(Awaken)):
			if len(Awaken[i].targets)!=0:
				closeRT = closestRobotInTargets(Awaken[i], w)
				if are_at_same_place(Awaken[i],closeRT) :
					awake_robot(w, i, closeRT)
					if len(Awaken[i].targets)!=0:
						TowardAwakeRobot(Awaken[i], closestRobotInTargets(Awaken[i], w))
				else:
					TowardAwakeRobot(Awaken[i], closestRobotInTargets(Awaken[i], w))
			iterations+=1
			print(iterations)
		
	return Sleeping
			
# print(test_execution())

def screenInit(world, psize):
	"""Initialize the screen"""
	pg.init()
	screen = pg.display.set_mode((world.N*psize, world.N*psize))
	pg.display.set_caption('Robots')
	screen.fill(pg.Color('black'))
	[pg.draw.circle(screen, pg.Color('red'), (psize*robot.x, psize*robot.y), psize//2) for robot in world.Awake]
	[pg.draw.circle(screen, pg.Color('blue'), (psize*robot.x, psize*robot.y), psize//2) for robot in world.Sleeping]
	return screen

if __name__ == "__main__":
	N = 50
	psize = 20
	w = World()
	w.init_world_from_file("test2.txt")
	w.init_target()
	screen = screenInit(w, psize)
	running = True
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
		screen.fill(pg.Color('black'))
		iterations = 0
		while len(w.Sleeping) > 0:
			for i in range(len(w.Awake)):
				screen.fill(pg.Color('black'))
				if len(w.Awake[i].targets)!=0:
					closeRT = closestRobotInTargets(w.Awake[i], w)
					if are_at_same_place(w.Awake[i],closeRT) :
						awake_robot(w, i, closeRT)
						# if len(w.Awake[i].targets)==0:
							
						# 	compute_sub_list(w.Awake[i], w.Awake[-1], closestRobot(w, w.Awake[i]))
						# 	print("After :" + str(len(closestRobot(w, w.Awake[i]).targets)))
							
					else:
						TowardAwakeRobot(w.Awake[i], closestRobotInTargets(w.Awake[i], w))
				iterations+=1
				print(iterations)
			for a in w.Awake:
				pg.draw.circle(screen, pg.Color('red'), (psize*a.x, psize*a.y), psize//2)

			for r in w.Sleeping:
				pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)

			pg.display.flip()
			pg.time.delay(300)
			#print(iterations)

		# TowardAwakeRobot(w.Awake, closestRobot(w, w.Awake))
		# robot = w.Awake[0]
		# TowardAwakeRobot(robot, closestRobot(w, robot))
		# for r in w.Sleeping:
		# 	pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)
		# closest = closestRobot(w, robot)
		# pg.draw.line(screen, (0,0,0), (robot.x*psize, robot.y*psize), (closest.x*psize, closest.y*psize))
		
		# screen.fill(pg.Color('black'))
		# robot = w.Awake[0]
		# TowardAwakeRobot(robot, closestRobot(w, robot))
		# pg.draw.circle(screen, pg.Color('red'), (psize*robot.x, psize*robot.y), psize//2)
		# for r in w.Sleeping:
		# 	pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)
		# closest = closestRobot(w, robot)
		# pg.draw.line(screen, (0,0,0), (robot.x*psize, robot.y*psize), (closest.x*psize, closest.y*psize), width=2)
		# pg.display.flip()
		# pg.time.wait(500)
	pg.quit()
	quit()
