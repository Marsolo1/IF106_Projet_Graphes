import numpy as np
import pygame as pg

class World:
	def __init__(self, Sleeping, N = None, Main = None, Obstacles=None):
		self.N = N
		self.Awake = Main
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles
	
	def init_world_from_file (self, filename):
		data = []
		f = open(filename, 'r')
		for line in f:
			l = line.strip().split(" : ")
			x = int(l[1].split(",")[0][1:])
			y = int (l[1].split(",")[1][:-1])
			#We suppose that there are only robots and no obstacles
			if l[0] == 'R':
				self.Awake = Robot("A", x, y)
			else:
				self.Sleeping.append(Robot("S", x, y))
		f.close()

class Robot:
	def __init__(self, type: str, x: int, y: int ,targets):
		self.type = type
		self.x = x
		self.y = y
		self.targets = targets

	def wakeUp(self):
		self.type = "A"

def TowardAwakeRobot(robotA, robotS):
	"""Advance a robot Awake of one pixel towards a sleeping robotS"""
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
			
print(test_execution())





if __name__ == "__main__":
	N = 20
	psize = 20
	w = World([], N)
	w.init_world_from_file("test.txt")
	pg.init()
	screen = pg.display.set_mode((N*psize, N*psize))
	clock = pg.time.Clock()
	running = True
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
		screen.fill((255,255,255))
		TowardAwakeRobot(w.Awake, closestRobot(w, w.Awake))
		pg.draw.rect(screen, (0,100,100), (w.Awake.x*psize, w.Awake.y*psize, psize, psize))
		for r in w.Sleeping:
			pg.draw.rect(screen, (255, 0, 0), (r.x*psize, r.y*psize, psize, psize))
		closest = closestRobot(w, w.Awake)
		pg.draw.line(screen, (0,0,0), (w.Awake.x*psize, w.Awake.y*psize), (closest.x*psize, closest.y*psize))
		pg.display.flip()
		pg.time.delay(1000)
		clock.tick(100)
	pg.quit()
	quit()
