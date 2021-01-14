from .utils import distancePoint
import numpy as np


def voisin_sommet(n, i, di):
    return (i+di) % n


def equation_droite(P0, P1, M):
    return (P1[0]-P0[0])*(M[1]-P0[1])-(P1[1]-P0[1])*(M[0]-P0[0])


def point_dans_triangle(triangle, M):
    P0 = triangle[0]
    P1 = triangle[1]
    P2 = triangle[2]
    return equation_droite(P0, P1, M) > 0 and equation_droite(P1, P2, M) > 0 and equation_droite(P2, P0, M) > 0


def point_dans_polygone(polygone, point):
    triangles = trianguler_polygone(polygone)
    for triangle in triangles:
        if point_dans_triangle(triangle, point):
            return True
    return False


def sommet_distance_maximale(polygone, P0, P1, P2, indices):
    n = len(polygone)
    distance = 0.0
    j = None
    for i in range(n):
        if not(i in indices):
            M = polygone[i]
            if point_dans_triangle([P0, P1, P2], M):
                d = abs(equation_droite(P1, P2, M))
                if d > distance:
                    distance = d
                    j = i
    return j


def sommet_gauche(polygone):
    n = len(polygone)
    x = polygone[0][0]
    j = 0
    for i in range(1, n):
        if polygone[i][0] < x:
            x = polygone[i][0]
            j = i
    return j


def nouveau_polygone(polygone, i_debut, i_fin):
    n = len(polygone)
    p = []
    i = i_debut
    while i != i_fin:
        p.append(polygone[i])
        i = voisin_sommet(n, i, 1)
    p.append(polygone[i_fin])
    return p


def trianguler_polygone_recursif(polygone, liste_triangles):
    n = len(polygone)
    # print(polygone)
    j0 = sommet_gauche(polygone)
    j1 = voisin_sommet(n, j0, 1)
    j2 = voisin_sommet(n, j0, -1)
    P0 = polygone[j0]
    P1 = polygone[j1]
    P2 = polygone[j2]
    j = sommet_distance_maximale(polygone, P0, P1, P2, [j0, j1, j2])
    if j == None:
        liste_triangles.append([P0, P1, P2])
        polygone_1 = nouveau_polygone(polygone, j1, j2)
        if len(polygone_1) == 3:
            liste_triangles.append(polygone_1)
        else:
            trianguler_polygone_recursif(polygone_1, liste_triangles)
    else:
        polygone_1 = nouveau_polygone(polygone, j0, j)
        polygone_2 = nouveau_polygone(polygone, j, j0)
        if len(polygone_1) == 3:
            liste_triangles.append(polygone_1)
        else:
            trianguler_polygone_recursif(polygone_1, liste_triangles)
        if len(polygone_2) == 3:
            liste_triangles.append(polygone_2)
        else:
            trianguler_polygone_recursif(polygone_2, liste_triangles)
    return liste_triangles


def trianguler_polygone(polygone):
    liste_triangles = []
    trianguler_polygone_recursif(polygone, liste_triangles)
    return liste_triangles


def surface(batiment):
    if len(batiment) == 3:
        A, B, C = batiment[0], batiment[1], batiment[2]
        a = distancePoint(B, C)
        b = distancePoint(A, C)
        c = distancePoint(A, B)
        P = a + b + c
        # Formule de Heron
        p = P/2
        S = np.sqrt(p*(p-a)*(p-b)*(p-c))
        return S
    else:
        triangles = trianguler_polygone(batiment)
        surfaces_triangles = [surface(triangle) for triangle in triangles]
        return sum(surfaces_triangles)


triangle = [[0, 0], [0, 1], [1, 0]]
carre = [[0, 0], [0, 1], [1, 0], [1, 1]]

polygone = [[0, 0], [0.5, -1], [1.5, -0.2],
            [2, -0.5], [2, 0], [1.5, 1], [0.3, 0, ], [0.5, 1]]
