import numpy as np
import sys
sys.setrecursionlimit(20000)
sys.settrace
import matplotlib.pyplot as plt

class Node:
    def __init__(self, data):
        self.data = data
        self.right = None
        self.left = None
        self.parent = None
        
    def __str__(self):
        return str(self.data) + ': {' + str(self.right) + ',' + str(self.left) + '}'
    
    def setChildren(self, left, right):
        self.right = right
        self.left = left

    def setParent(self, parent):
        self.parent = parent


def mediane_des_medianes(points):
    points = list2dict(points)
    n = len(points)
    while n > 5:
        medianes = {}
        groupe = {}
        for k,i in enumerate(points.keys()):
            groupe[i] = points[i]
            if k % 5 == 4:
                median, index = mediane(groupe)
                medianes[index] = median
                groupe = {}
        if len(groupe) > 0:
            median, index = mediane(groupe)
            medianes[index] = median
        points = medianes
        n = len(points)
    return mediane(points)


def mediane(groupe):
    n = len(groupe)
    if n == 0:
        return None
    sort = sorted(groupe.values())
    median = sort[n//2]
    index = 0
    for i in groupe.keys():
        if groupe[i] == median:
            index = i
    return sort[n//2], index



def list2dict(liste):
    if type(liste) == dict:
        return liste
    res = {}
    for k in range(len(liste)):
        res[k] = liste[k]
    return res

# n = 10000
# points = range(n)
# print(mediane_des_medianes(points))


def mediane_direction(points, direction):
    x, y = {},{}
    for i in points.keys():
        x[i], y[i] = points[i]
    if not direction:
        return mediane_des_medianes(x)
    else:
        return mediane_des_medianes(y)


def arbreKd(points, direction=0, racine=Node(None)):
    points = list2dict(points)
    if len(points) == 0:
        return None
    median, index = mediane_direction(points, direction)
    res = Node(index)
    res.parent = racine
    low, high = {},{}
    for i in points.keys():
        if points[i][direction] < median:
            low[i] = points[i]
        if points[i][direction] > median:
            high[i] = points[i]
    res.setChildren(arbreKd(low, 1-direction, res), arbreKd(high, 1-direction, res))
    return res

    

def insert(point, arbre, points, parent=Node(None), direction=0):
    if arbre == None:
        return parent, direction
    else:
        if point[direction] < points[arbre.data][direction]:
            node = arbre.left
        else: 
            node = arbre.right
        if node == None:
            return arbre, direction
        return insert(point, node, points, node.parent, 1-direction)

def distance(point1, point2):
    return np.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def plus_proche_voisin(point, points):
    arbre = arbreKd(points)
    node, direction = insert(point, arbre, points)
    bestDist = float("inf")
    while node.data != None:
        dist = distance(point, points[node.data])
        median = points[node.data][direction]
        if dist < bestDist:
            bestDist = dist
            best = node
        if abs(median-point[direction]) < bestDist:
            if node == node.parent.right:
                if node.parent.left != None:
                    node = node.parent.left
            elif node == node.parent.left: 
                if node.parent.right != None:
                    node = node.parent.right
            dist = distance(point, points[node.data])
            if dist < bestDist:
                bestDist = dist
                best = node
                node, direction = insert(point, node, points)
        node = node.parent
        direction = 1-direction
    return best

        
# points = np.random.random((n, 2))

# point = np.random.random(2)
# print(point)
# voisin = plus_proche_voisin(point, points)
# print(voisin)

# x, y = [point[0] for point in points], [point[1] for point in points]
# plt.scatter(x, y, color="blue")
# plt.scatter(point[0], point[1], color="red")
# plt.scatter(points[voisin.data][0], points[voisin.data][1], color="green")
# plt.show()