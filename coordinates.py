
import geocoder

def getLocationFromAddress(address):
    g = geocoder.osm(address)
    latlng = g.latlng
    if latlng != None and len(latlng) == 2:
        return [latlng[1], latlng[0]]
    else: 
        return None

getLocationFromAddress("118 impasse des prés de jonquières 84450")