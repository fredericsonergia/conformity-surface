import json
import gzip
import matplotlib.pyplot as plt
import requests
import os
import numpy as np
import time

# print("\033c")

date = "latest"


def getVille(coordinates):
    DATA = {"geom": {"type": "Point", "coordinates": coordinates}}
    URL = "https://apicarto.ign.fr/api/gpu/municipality"
    res = requests.get(url=URL, json=DATA)
    variant = "gpu"
    try:
        res.json()
    except:
        URL = "https://apicarto.ign.fr/api/cadastre/commune"
        res = requests.get(url=URL, json=DATA)
        variant = "cadastre"
        res.json()
    print(variant)
    if res == None:
        return None, None
    else: 
        res = res.json()
        if variant == "gpu2" and len(res)>1:
            res = res[0]
        elif len(res) < 2:
            return None, None
    maxLength = 0
    if res['totalFeatures'] == 0:
        return None, None
    for feature in res["features"]:
        properties = feature["properties"]
        name = properties["name"] if variant[:3] == "gpu" else properties["nom_com"]
        length = len(name)
        if length > maxLength:
            maxLength = length
            content = properties
    return content["name"] if variant[:3] == "gpu" else content["nom_com"], content["insee"] if variant[:3] == "gpu" else content["code_insee"]

def retrieveData(dep, output):
    start = time.time()
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
    try:
        the_file = gzip.open("./data/" + archivePath, 'rb')
    except gzip.BadGzipFile:
        print("No archive found")
        return None
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
    return time.time() - start

def getData(dep, MAJ=False):
    dt = 0
    output = "cadastre-"+dep+"-batiments.json"
    if not os.path.exists("data/" + output):
        open("data/" + output, "w")

    with open("./data/" + output) as f:
        if len(f.readline()) == 0 or MAJ:
            if MAJ:
                print("updating the data ... ")
            else:
                print("retrieving data ...")
            dt = retrieveData(dep, output)
            print("done")
        else:
            print("data already retrieved")

    with open("./data/" + output) as json_file:
        data = json.load(json_file)
    return data, dt


