import numpy as np
import pygame as pg

class World:
	def __init__(self, N = 0, Sleeping = [], Main = [], Edges = [], Obstacles=None):
		self.N = N
		self.Awake = Main
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles
		self.Edges = Edges
	
	def init_world_from_file (self, N, filename):
		self.N = N
		f = open(filename, 'r')
		for line in f:
			l = line.strip().split(" : ")
			x = int(l[1].split(",")[0][1:])
			y = int (l[1].split(",")[1][:-1])
			#We suppose that there are only robots and no obstacles
			if l[0] == 'R':
				self.Awake.append(Robot("A", x, y))
			elif l[0].isnumeric():
				self.Sleeping.append(Robot("S", x, y))
			elif l[0] == 'E':
				self.Edges.append(
					(self.Awake[0] if x != 'R' else self.Sleeping[int(x)],
					self.Awake[0] if y != 'R' else self.Sleeping[int(y)]))

		f.close()

	def init_target(self):
		for r in self.Awake:
			r.targets = self.Sleeping
		print(self.Awake)

class Robot:
	def __init__(self, type: str, x: int, y: int ,targets = None):
		self.type = type
		self.x = x
		self.y = y
		self.targets = targets

	def wakeUp(self):
		self.type = "A"

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
			x_max, y_max = robotA.x, robotA.y
			r = robot
	return r

def closestRobotInTargets(robotA, world):
	"""Look for the closest robot"""
	n = world.N
	x_max, y_max = n, n
	r = None
	for robot in robotA.targets:
		diff_x = abs(robot.x - robotA.x)
		diff_y = abs(robot.y - robotA.y)
		if (x_max + y_max > diff_x + diff_y):
			x_max, y_max = robotA.x, robotA.y
			r = robot
	return r

def compute_sub_list(robota,robotb):
	def compute_coef(robota,robotb):
		def compute_affine(xa,xb,ya,yb):
			a=(yb-ya)/(xb-xa)
			b=ya-a*xa
			return [a,b]
		return compute_affine(robota.x,robotb.x,robota.y,robotb.y)
	def separate(T,a,b):
		T1=[]
		T2=[]
		for i in range(len(T)):
			if T[i].y >= a*T[i].x+b:
				T1.append(T[i])
			else :
				T2.append(T[i])
		return [T1,T2]
	T=robota.targets
	if robota.x != robotb.x:
		robota.targets=separate(T,compute_coef(robota,robotb)[0],compute_coef(robota,robotb)[1])[0]
		robotb.targets=separate(T,compute_coef(robota,robotb)[0],compute_coef(robota,robotb)[1])[1]
	else :
		robota.targets=[]
		robotb.targets=[]
		for i in range(len(T)):
			if T[i].x > robota.x:
				robota.targets.append(T[i])
			else:
				robotb.targets.append(T[i])
	return

def are_at_same_place(robota,robotb):
	return (robota.x==robotb.x and robota.y==robotb.y)

def remove_from_sleeping(Awaken,Sleeping,robot):
	for i in range(len(Sleeping)):
		if Sleeping[i]==robot:
			Awaken.append(robot)
			Sleeping.pop(i)
	return

def remove_from_targets(robotA,robotB):
	for i in range(len(robotA.targets)):
		if robotA.targets[i]==robotB:
			robotA.targets.pop(i)
	return

def test_execution():
	N = 20
	Sleeping = [Robot('S',x, y, targets) for (x,y,targets) in [[0, 5, []], [5, 6, []], [12, 7, []]]]
	S = len(Sleeping)
	Main = Robot("A", N//2, N//2, Sleeping)
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
				if are_at_same_place(Awaken[i],closestRobotInTargets(Awaken[i], w)) :
					remove_from_sleeping(Awaken,Sleeping,closestRobotInTargets(Awaken[i], w))
					closestRobotInTargets(Awaken[i], w).wakeUp
					Awaken[len(Awaken)-1].wakeUp
					remove_from_targets(Awaken[i],closestRobotInTargets(Awaken[i], w))
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
	w.init_world_from_file(N, "test2.txt")
	w.init_target()
	screen = screenInit(w, psize)
	running = True
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
		screen.fill((255,255,255))
		iterations = 0
		while len(w.Sleeping) > 0:
			if iterations == 0 :
				compute_sub_list(w.Awake[0],closestRobot(w, w.Awake[0]))
				print(w.Awake[0].targets)
				print(closestRobot(w, w.Awake[0]))
			for i in range(len(w.Awake)):
				screen.fill((255,255,255))

				if len(w.Awake[i].targets)!=0:
					if are_at_same_place(w.Awake[i],closestRobotInTargets(w.Awake[i], w)) :
						remove_from_sleeping(w.Awake,w.Sleeping,closestRobotInTargets(w.Awake[i], w))
						closestRobotInTargets(w.Awake[i], w).wakeUp
						w.Awake[len(w.Awake)-1].wakeUp
						remove_from_targets(w.Awake[i],closestRobotInTargets(w.Awake[i], w))
						if len(w.Awake[i].targets)!=0:
							TowardAwakeRobot(w.Awake[i], closestRobotInTargets(w.Awake[i], w))
					else:
						TowardAwakeRobot(w.Awake[i], closestRobotInTargets(w.Awake[i], w))
				iterations+=1
				for a in w.Awake:
					pg.draw.circle(screen, pg.Color('red'), (psize*a.x, psize*a.y), psize//2)

				for r in w.Sleeping:
					pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)

				pg.display.flip()
				pg.time.delay(1000)
				print(iterations)

		# TowardAwakeRobot(w.Awake, closestRobot(w, w.Awake))
		# robot = w.Awake[0]
		# TowardAwakeRobot(robot, closestRobot(w, robot))
		# for r in w.Sleeping:
		# 	pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)
		# closest = closestRobot(w, robot)
		# pg.draw.line(screen, (0,0,0), (robot.x*psize, robot.y*psize), (closest.x*psize, closest.y*psize))
		
	pg.quit()
	quit()
