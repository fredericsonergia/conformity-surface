from conversion import gps2Lambert, gps2zone
import matplotlib.pyplot as plt
from PIL import Image 
import numpy as np



# get the image from the internet
w = 800
h = 400

r = 6

W = w/r
H = h/r

x = 4.863327
y = 45.853052

coords = (x, y)
X, Y = gps2Lambert(coords)

bbox = (X - W/2, Y - H/2, X + W/2, Y + H/2)
# bbox = (1844637.6108677688,5185333.742173912,1844774.3197933885,5185398.953913044)

print(bbox)

def getImage(w, h, bbox):
    pass

def rotation(theta, coordinates):
    x,y = coordinates
    Deltax = y * np.sin(theta) + x * (np.cos(theta) - 1)
    Deltay = y * (np.cos(theta) - 1) - x * np.sin(theta)
    return np.array(coordinates) + np.array()

img = Image.open(r'data/response.png')

coordinates = [[4.863412, 45.8529598], [4.8634738, 45.852981], [4.8634597, 45.8530018], [4.8634461, 45.8530221], [4.8634862, 45.8530355], [4.8635604, 45.8530604], [4.8635096, 45.853134], [4.8634904, 45.8531276], [4.8634983, 45.8531162], [4.8634042, 45.8530834], [4.8633956, 45.8530958], [4.8633764, 45.8530894], [4.8633622, 45.8531102], [4.863319, 45.8530961], [4.863412, 45.8529598]]
batiment = [gps2Lambert(np.array(coord)) - np.array([49, 30])/(1*r)  for coord in coordinates]
batX, batY = [r*(coord[0] - bbox[0]) for coord in batiment], [r*(coord[1] - bbox[1]) for coord in batiment]
fig, ax = plt.subplots()
x = range(300)
ax.imshow(img, extent=[0, w, 0, h])
ax.plot(batX, batY, color='firebrick')
plt.show()

# 1844637.6108677688,5185333.742173912,1844774.3197933885,5185398.953913044
# print(1844637 + W, 5185333+ H)