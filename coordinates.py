
import geocoder

def getLocationFromAddress(address):
    g = geocoder.osm(address)
    latlng = g.latlng
    return [latlng[1], latlng[0]]
