import numpy as np


a = 6378388
a = a - 209.75
b = 6356752

RT = 6371008


f = (a-b)/a
e = np.sqrt(1 - (b/a)**2)
e = 0.08199188998

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
    return zone


def n(zone):
    phi1 = (zone - 0.75) * np.pi / 180
    phi2 = (zone + 0.75) * np.pi / 180
    n1 = np.log(np.cos(phi1)/np.cos(phi2)) + 1/2 * \
        np.log((1 - e**2 * np.sin(phi1)**2)/(1 - e**2 * np.sin(phi2)**2))
    n2 = np.log(np.tan(phi1/2 + np.pi/4)/np.tan(phi2/2 + np.pi/4) * (((1 - e*np.sin(phi1)) /
                                                                      (1 - e*np.sin(phi2)))**(e/2)) * (((1 + e*np.sin(phi2))/(1 + e*np.sin(phi1)))**(e/2)))
    return n1 / n2

# print(n(46))


def rho0(zone):
    phi1 = (zone - 0.75) * np.pi / 180
    phi2 = (zone + 0.75) * np.pi / 180
    rho1 = a * np.cos(phi1)/(n(zone) * np.sqrt((1 - (e * np.sin(phi1))**2)))
    rho2 = (np.tan(phi1/2 + np.pi/4) * ((1 - e * np.sin(phi1)) /
                                        (1 + e * np.sin(phi1)))**(e/2)) ** n(zone)
    return rho1*rho2


def rho(phi, zone):
    rho1 = (1 / np.tan(phi/2 + np.pi/4) * ((1 + e * np.sin(phi)) /
                                           (1 - e * np.sin(phi)))**(e/2)) ** n(zone)
    return rho1*rho0(zone)


def gps2zone(coordinatesDegre):
    zone = getZone(coordinatesDegre)
    zone = 46
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
    zone = 46
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
    return X, Y


def latitudeIso(phi):
    return np.log((np.tan(np.pi/4 + phi/2))*((1-e*np.sin(phi))/(1+e*np.sin(phi)))**(e/2))


def grande_normale(phi):
    return a / np.sqrt(1 - e**2 * np.sin(phi)**2)


def lambert(lmb, phi):
    L = latitudeIso(phi)
    lmb0 = 3 * np.pi/180
    zone = getZone((lmb * 180/np.pi, phi * 180/np.pi))
    phi2 = (zone - 0.75) * np.pi / 180
    phi1 = (zone + 0.75) * np.pi / 180
    phi0 = zone * np.pi/180
    X0 = 1700000
    Y0 = ((zone-41)*1000000) + 200000
    n, C, Xs, Ys = parametres_de_projection(phi0, lmb0, phi1, phi2, X0, Y0)
    X = Xs + C * np.exp(- n * L) * np.sin(n * (lmb - lmb0))
    Y = Ys - C * np.exp(- n * L) * np.cos(n * (lmb - lmb0))
    return X, Y


def parametres_de_projection(phi0, lmb0, phi1, phi2, X0, Y0):
    n = (np.log((grande_normale(phi2)*np.cos(phi2))/(grande_normale(phi1)
                                                     * np.cos(phi1))))/(latitudeIso(phi1) - latitudeIso(phi2))
    C = grande_normale(phi1) * np.cos(phi1)/n * np.exp(n * latitudeIso(phi1))
    Xs, Ys = X0, Y0
    if abs(phi0 - np.pi/2) < 1E-4:
        Xs, Ys = X0, Y0
    else:
        Xs = X0
        Ys = Y0 + C * np.exp(-n*latitudeIso(phi0))
    return n, C, Xs, Ys


def degre2rad(angle):
    return angle*np.pi/180
