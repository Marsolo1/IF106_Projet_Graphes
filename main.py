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
	def __init__(self, type: str, x: int, y: int):
		self.type = type
		self.x = x
		self.y = y
	
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
