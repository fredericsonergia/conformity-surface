
from main import main
import numpy as np
import matplotlib.pyplot as plt
from closest import closestBuilding, closestCenter
import time

with open("201216_Fichier Cadastre surface.csv", 'r') as f:
    lines = f.readlines()

def getInfos(line):
    splitted = line.lower().split(';')
    for a in splitted[0]:
        if a not in '0123456789':
            print("Not a line")
            return None
    if len(splitted) < 5 : 
        return None  
    address = splitted[1].split(":")[0].split("parcelle")[0] + ', ' + splitted[2]
    surface = splitted[5]
    eps = 1 if "e" in splitted[8] else -1
    coords = [eps*float(splitted[7].replace(',', '.')),float(splitted[6].replace(',', '.'))]
    if surface == '':
        print("Surface NaN")
        return None
    for a in surface: 
        if a not in '0123456789':
            print("Surface NaN")
            return None
    return address, float(surface), coords

infos = [getInfos(line) for line in lines]

res = []
Max = 0
start = time.time()
for info in infos:
    if info != None:
        errors = main(info, closestBuilding)
        res.append(np.sqrt(errors[0]))
        if errors != None and errors[1] > Max:
            Max = errors[1]
print(time.time() - start)
plt.hist(res, range=(0, max(res)), bins=50)
mseSurf = 0
i = 0
for errors in res:
    if  errors != None:
        mseSurf += errors
        i += 1
# print(np.sqrt(Max))
print(np.sqrt(mseSurf)/i)
plt.show()
# print(np.sqrt(mseCoord)/i)


print("\n DONE \n")
# print(res)