import numpy as np
import matplotlib.pyplot as plt

Awake = 0


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
