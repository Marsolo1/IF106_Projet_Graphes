import numpy as np
import matplotlib.pyplot as plt

Awake = 0

def makeWorld(N, Main, Sleeping, Obstacles):
	"""
	Creates a world with NxN cells and Robots robots.
	"""
	world = np.ndarray.fill(np.ndarray(shape=(N,N)), "")
	world[Main[0]][Main[1]] = "M"+str(Awake)
	Awake += 1
	for r in Sleeping:
		world[r[0],r[1]] += ""
	for o in Obstacles:
		world[o[0],o[1]] = -1