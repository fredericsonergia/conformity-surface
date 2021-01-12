import numpy as np


a = 6378137
b = 6356752

RT = 6371008
# f = 1/298.257223563
# print(f)
f = (a-b)/a
e = np.sqrt(2 * f - f**2)

longueur1degre = RT*np.pi/180


def gps2plan(coordinatesDegre):
    xDeg, yDeg = coordinatesDegre
    y = yDeg * longueur1degre
    x = xDeg * np.cos(yDeg*np.pi/180) * longueur1degre
    return x, y


def buildingGPS2plan(building):
    return [gps2plan(coord) for coord in building]


def getZone(coordinatesDegre):
    lng, lat = coordinatesDegre
    mini = 1
    for i in range(42, 51):
        if abs(lat - i) < mini:
            mini = abs(lat - i)
            zone = i
        # if abs(lat - (i + 0.75)) < mini:
        #     mini = abs(lat - (i + 0.75))
        #     zone = i
        # if abs(lat - (i - 0.75)) < mini:
        #     mini = abs(lat - (i - 0.75))
        #     zone = i
    return zone


def n(zone):
    phi1 = (zone - 0.75) * np.pi / 180
    phi2 = (zone + 0.75) * np.pi / 180
    n1 = np.log(np.cos(phi1)/np.cos(phi2)) + 1/2 * \
        np.log((1 - e**2 * np.sin(phi1)**2)/(1 - e**2 * np.sin(phi2)**2))
    n2 = np.log(np.tan(phi1/2 + np.pi/4)/np.tan(phi2/2 + np.pi/4) * (((1 - e*np.sin(phi1))/(1 - e*np.sin(phi2)))**(e/2)) * (((1 + e*np.sin(phi2))/(1 + e*np.sin(phi1)))**(e/2)))
    return n1 / n2

# print(n(46))

def rho0(zone):
    phi1 = (zone - 0.75) * np.pi / 180
    phi2 = (zone + 0.75) * np.pi / 180
    N = n(zone)
    rho1 = a * np.cos(phi1)/(N * np.sqrt((1 - (e * np.sin(phi1))**2)))
    rho2 = (np.tan(phi1/2 + np.pi/4) * ((1 - e * np.sin(phi1))/ (1 + e * np.sin(phi1)))**(e/2)) ** N
    return rho1*rho2

def rho(phi, zone):
    rho1 = (1 / np.tan(phi/2 + np.pi/4) * ((1 + e * np.sin(phi)) / (1 - e * np.sin(phi)))**(e/2)) ** n(zone)
    return rho1*rho0(zone)

# print(rho0(42))

# print(rho(42.2*np.pi/180,42))


def gps2zone(coordinatesDegre):
    zone = getZone(coordinatesDegre)
    # calcul de R(phi0)
    phi1, phi2 = zone + 0.75, zone - 0.75
    R0 = RT*np.cos((phi1-phi2)/2) * np.tan(zone * np.pi/180)
    lng, lat = coordinatesDegre
    X0 = 1700000
    Y0 = ((zone-41)*1000000) + 200000
    phi = (lat - zone) * np.pi/180
    psi = (lng - 3) * np.pi/180
    y = RT * np.sin(phi) + R0 * (1 - np.cos(psi)) + Y0
    x = (R0 - RT * np.sin(phi)) * np.sin(psi) + X0
    return x, y

def gps2Lambert(coordinatesDegre):
    zone = getZone(coordinatesDegre)  
    lng, lat = coordinatesDegre
    X0 = 1700000
    Y0 = ((zone-41)*1000000) + 200000
    phi = lat * np.pi/180
    phi0 = zone * np.pi/180
    lmb = (lng - 3) * np.pi/180
    theta = n(zone) * lmb
    Rho = rho(phi, zone)
    Rho0 = rho(phi0, zone)
    X = X0 + Rho * np.sin(theta)
    Y = Y0 + Rho0 - Rho * np.cos(theta)
    return X,Y

# X1, Y1 = gps2Lambert((3, 46))
# X2, Y2 = gps2zone((4.863327, 45.853052))
# print((X1,Y1),(X2,Y2))
