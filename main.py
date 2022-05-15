import pygame as pg
import sys

class World:
	def __init__(self, N:int=0, Sleeping:list=[], Main:list=[], Edges:list=[], Obstacles:list=[]):
		self.N = N
		self.Awake = Main
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles
		self.Edges = Edges

	def init_world_from_file(self, filename):
		f = open(filename, 'r')
		for line in f:
			l = line.strip().split(" : ")
			x = l[1].split(",")[0][1:]
			y = l[1].split(",")[1][:-1]
			# We suppose that there are only robots and no obstacles
			if l[0] == 'R':
				self.Awake.append(Robot("A", int(x), int(y)))
			elif l[0].isnumeric():
				self.Sleeping.append(Robot("S", int(x), int(y)))
			elif l[0] == 'E':
				self.Edges.append((
					self.Awake[0] if x == 'R' else self.Sleeping[int(x)-1],
					self.Awake[0] if y == 'R' else self.Sleeping[int(y)-1]
				))
		f.close()
		self.N = max([self.Awake[0].x, self.Awake[0].y] +
					 [r.x for r in self.Sleeping] + [r.y for r in self.Sleeping]) + 1

	def update(self, screen: pg.Surface, psize: int):
		screen.fill(pg.Color("lightgray"))
		for r in self.Awake:
			pg.draw.circle(screen, pg.Color('red'), (r.x*psize, r.y*psize), psize//2)
		for r in self.Sleeping:
			pg.draw.circle(screen, pg.Color('blue'), (r.x*psize, r.y*psize), psize//2)
			

class Robot:
	def __init__(self, type: str, x: int, y: int, targets:list=[]):
		self.type = type
		self.x = x
		self.y = y
		self.targets = targets

	def wakeUp(self):
		self.type = "A"


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
			x_max, y_max = robotA.x, robotA.y
			r = robot
	return r


def compute_sub_list(robota: Robot, robotb: Robot) -> list:
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
		return [T1, T2]
	T = robota.targets
	if robota.x != robotb.x:
		robota.targets = separate(T, compute_coef(robota, robotb)[
								  0], compute_coef(robota, robotb)[1])[0]
		robotb.targets = separate(T, compute_coef(robota, robotb)[
								  0], compute_coef(robota, robotb)[1])[1]
	else:
		robota.targets = []
		robotb.targets = []
		for i in range(len(T)):
			if T[i].x > robota.x:
				robota.targets.append(T[i])
			else:
				robotb.targets.append(T[i])
	return


def are_at_same_place(robota: Robot, robotb: Robot) -> bool:
	return (robota.x == robotb.x and robota.y == robotb.y)


def remove_from_sleeping(Awaken: list, Sleeping: list, robot: Robot):
	for i in range(len(Sleeping)):
		if Sleeping[i] == robot:
			Awaken.append(robot)
			Sleeping.pop(i)
	return

def wakeUp(world: World, robot: Robot):
	robot.wakeUp()
	world.Sleeping.remove(robot)
	world.Awake.append(robot)

def remove_from_targets(robotA: Robot, robotB: Robot):
	for i in range(len(robotA.targets)):
		if robotA.targets[i] == robotB:
			robotA.targets.pop(i)
	return


def test_execution():
	N = 20
	Sleeping = [Robot('S', x, y, targets) for (x, y, targets)
				in [[0, 5, []], [5, 6, []], [12, 7, []]]]
	S = len(Sleeping)
	Main = Robot("A", N//2, N//2, Sleeping)
	Awaken = [Main]
	w = World(N, Awaken[0], Sleeping)
	iterations = 0
	while len(Awaken) <= S:
		if iterations == 0:
			compute_sub_list(Awaken[0], closestRobot(w, Awaken[0]))
			print(Awaken[0].targets)
			print(closestRobot(w, Awaken[0]))
		for i in range(len(Awaken)):
			if len(Awaken[i].targets) != 0:
				if are_at_same_place(Awaken[i], closestRobotInTargets(Awaken[i], w)):
					remove_from_sleeping(
						Awaken, Sleeping, closestRobotInTargets(Awaken[i], w))
					closestRobotInTargets(Awaken[i], w).wakeUp
					Awaken[len(Awaken)-1].wakeUp
					remove_from_targets(
						Awaken[i], closestRobotInTargets(Awaken[i], w))
					if len(Awaken[i].targets) != 0:
						TowardAwakeRobot(
							Awaken[i], closestRobotInTargets(Awaken[i], w))
				else:
					TowardAwakeRobot(
						Awaken[i], closestRobotInTargets(Awaken[i], w))
			iterations += 1
			print(iterations)

	return Sleeping


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


if __name__ == "__main__":
	N = 20
	
	psize = 20
	w = World()
	w.init_world_from_file(sys.argv[1])
	screen = screenInit(w, psize)
	stupidTravellingSalesman(w, screen, psize)
	pg.quit()
	quit()
