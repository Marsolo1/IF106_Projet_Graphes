import numpy as np
import pygame as pg

Awake = 0


class World:
	def __init__(self, N, Main, Sleeping, Obstacles=None):
		self.N = N
		self.World = np.zeros((N, N))
		self.Main = Main
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles


class Robot:
	def __init__(self, type: str, x: int, y: int):
		self.type = type
		self.x = x
		self.y = y


def makeWorld(N, Main, Sleeping, Obstacles):
	"""
	Creates a world with NxN cells and Robots robots.
	"""
	global Awake
	world = np.ndarray.fill(np.ndarray(shape=(N, N)), "")
	world[Main[0]][Main[1]] = "M"+str(Awake)
	Awake += 1
	for r in Sleeping:
		world[r[0], r[1]] += "S"
	for o in Obstacles:
		world[o[0], o[1]] = -1

	return world


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
			robotS.y -= 1
		if diff_y < 0:
			robotS.y += 1


def closestRobot(world, robotA):
	"""Look for the closest robot"""
	n = len(world.world)
	x_max, y_max = n, n
	r = None
	for robot in world.Sleeping:
		diff_x = abs(robot.x - robotA.x)
		diff_y = abs(robot.y - robotA.y)
		if (x_max + y_max > diff_x + diff_y):
			x_max, y_max = robotA.x, robotA.y
			r = robot
	return r


if __name__ == "__main__":
	N = 20
	psize = 20
	Main = [10, 10]
	Sleeping = [[0, 5], [5, 6], [12, 7]]
	w = World(N, Main, Sleeping)
	pg.init()
	screen = pg.display.set_mode((N*psize, N*psize))
	clock = pg.time.Clock()
	running = True
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
		screen.fill((255, 255, 255))
		pg.draw.rect(screen, (0, 100, 100),
					 (w.Main[0]*psize, w.Main[1]*psize, psize, psize))
		for r in w.Sleeping:
			pg.draw.rect(screen, (255, 0, 0),
						 (r[0]*psize, r[1]*psize, psize, psize))
		pg.display.flip()
		clock.tick(60)
	pg.quit()
	quit()
