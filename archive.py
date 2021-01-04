import json
import gzip
import matplotlib.pyplot as plt
import requests
import os
import numpy as np

# print("\033c")

date = "latest"


def getVille(coordinates):
    URL = "https://apicarto.ign.fr/api/gpu/municipality"
    DATA = {"geom": {"type": "Point", "coordinates": coordinates}}
    res = requests.get(url=URL, json=DATA)
    maxLength = 0
    for feature in res.json()["features"]:
        properties = feature["properties"]
        length = len(properties["name"])
        if length > maxLength:
            maxLength = length
            content = properties
    return content["name"], content["insee"]

def retrieveData(dep, output):
    print("Downloading archive ... ")
    archivePath = 'cadastre-'+dep+'-batiments.json.gz'
    if len(dep) == 2:
        req = requests.get(
            "https://cadastre.data.gouv.fr/data/etalab-cadastre/" + date + "/geojson/departements/" + dep + "/" + archivePath)
    else:
        req = requests.get("https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/communes/" +
                           dep[:2] + "/" + dep + "/" + archivePath)
    with open("./data/" + archivePath, 'wb') as fp:
        fp.write(req.content)
    the_file = gzip.open("./data/" + archivePath, 'rb')
    final_doc = ""
    print("Extracting archive ... ")
    for line in the_file:
        if type(line) is str:
            final_doc += line
        elif type(line) is bytes:
            final_doc += line.decode('utf_8', 'ignore')
    f = open("./data/" +output, "w")
    f.write(final_doc)
    f.close()
    the_file.close()
    if os.path.exists("./data/" + archivePath):
        os.remove("./data/" + archivePath)
    else:
        print("The file does not exist")

def getData(dep, MAJ=False):
    output = "cadastre-"+dep+"-batiments.json"
    if not os.path.exists("data/" + output):
        open("data/" + output, "w")

    with open("./data/" + output) as f:
        if len(f.readline()) == 0 or MAJ:
            if MAJ:
                print("updating the data ... ")
            else:
                print("retrieving data ...")
            retrieveData(dep, output)
            print("done")
        else:
            print("data already retrieved")

    with open("./data/" + output) as json_file:
        data = json.load(json_file)
    return data


