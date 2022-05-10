from msilib.schema import Class
import numpy as np
import matplotlib.pyplot as plt
import pygame as pg

Awake = 0


class World:
    def __init__(self, N, Main, Sleeping, Obstacles):
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

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy


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
    N = 10
    pg.init()
    screen = pg.display.set_mode((N*50, N*50))
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0, 0, 0))
        pg.display.flip()
        clock.tick(60)
    pg.quit()
    quit()
