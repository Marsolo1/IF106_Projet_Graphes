import numpy as np
import pygame as pg

class World:
	def __init__(self, N, Main, Sleeping, Obstacles=None):
		self.N = N
		self.Main = Main
		self.Sleeping = Sleeping
		self.Obstacles = Obstacles

class Robot:
    def __init__(self, type: str, x: int, y: int):
        self.type = type
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy



def TowardAwakeRobot(robotA, robotS):
    xa = robotA[0]
    ya = robotA[1]

    xs = robotS[0]
    ys = robotS[1]

    diff_x = xa-xs
    diff_y = ya-ys

    if abs(diff_x) > abs(diff_y):
        if diff_x > 0:
            xa -= 1
        if diff_x < 0:
            xa += 1
    else:
        if diff_y > 0:
            ya -= 1
        if diff_y < 0:
            ya += 1

    return [xa, ya]


def closestRobot(world, robotA):
    """Look for the closest robot"""
    n = len(world)
    arr = [n, n]
    for i in range(n):
        for j in range(n):
            if world[i, j] != "":
                rs = robotA, world[i, j]
                diff_x = abs(rs[0] - robotA[0])
                diff_y = abs(rs[1] - robotA[1])
                if (arr[n] + arr[n] > diff_x + diff_y):
                    arr = [rs[0], rs[1]]

    return arr
    # Penser à faire à map
    return 0


if __name__ == "__main__":
	N = 20
	psize = 20
	Main = Robot("A", N//2, N//2)
	Sleeping = [Robot('S',x, y) for (x,y) in [[0, 5], [5, 6], [12, 7]]]
	w = World(N, Main, Sleeping)
	pg.init()
	screen = pg.display.set_mode((N*psize, N*psize))
	clock = pg.time.Clock()
	running = True
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
		screen.fill((255,255,255))
		pg.draw.rect(screen, (0,100,100), (w.Main.x*psize, w.Main.y*psize, psize, psize))
		for r in w.Sleeping:
			pg.draw.rect(screen, (255, 0, 0), (r.x*psize, r.y*psize, psize, psize))
		pg.display.flip()
		clock.tick(60)
	pg.quit()
	quit()
