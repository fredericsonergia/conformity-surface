from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import json
import pickle
import configparser

import sys

sys.path.append('../')

from surface_estimator import SurfaceController
from surface_estimator.computer_vision.combine_solutions import SolutionCombiner
import uvicorn
from src.surface_estimator.getImage import ImagesController
from src.surface_estimator.IGN_API import IGN_API


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
Recover the configuration file 
"""
config = configparser.ConfigParser()
config.read("../surface.config")
Image, Confidence, Data = config['IMAGE'], config['CONFIDENCE'], config["DATA"]
w, h, r, R = int(Image["width in px"]), int(Image["height in px"]), float(
    Image["ratio in px/m"]), float(Image["Radius in m"])
data_path, static_path = Data["data_path"], Data["static_path"]
loaded_model = pickle.load(open(Confidence["path"], 'rb'))


"""
Define the data classes
"""


class coordsRequest(BaseModel):
    coordinates: str


class addressRequest(BaseModel):
    address: str


class BasicResponse(BaseModel):
    surface: float
    coords: list
    fileName: str


class FullResponse(BaseModel):
    surface: float
    coords: list
    fileName: str
    contours: list
    surfaces: list
    metrics: list


"""
Define the routes
"""

app.mount("/static", StaticFiles(directory=static_path), name="static")



@app.post("/estimateSurface/coordinates", response_model=BasicResponse)
def estimateSurface_coords(req: coordsRequest):

    coordinates = [float(coord) for coord in req.coordinates.split(',')]
    imgCtrl = ImagesController(static_path)
    ign = IGN_API(data_path)
    controller = SurfaceController(imgCtrl, ign)
    controller.set_coordinates(coordinates)
    controller.set_surface()
    controller.get_image(w, h)
    response = {"surface": controller.computedSurf,
                "coords": controller.image_coordinates, "fileName": controller.file_name[1:]}
    return response


@ app.post("/estimateSurface/address", response_model=BasicResponse)
def estimateSurface_address(req: addressRequest):

    address = req.address
    imgCtrl = ImagesController(static_path)
    ign = IGN_API(data_path)
    controller = SurfaceController(imgCtrl, ign)
    controller.set_address(address)
    controller.set_surface()
    controller.get_image(w, h)
    response = {"surface": controller.computedSurf,
                "coords": controller.image_coordinates, "fileName": controller.file_name[1:]}
    return response


@ app.post("/estimateSurface/coordinates/fromCV", response_model=FullResponse)
def estimateSurface_coords_from_cv(req: coordsRequest):

    coordinates = [float(coord) for coord in req.coordinates.split(',')]
    imgCtrl = ImagesController(static_path)
    ign = IGN_API(data_path)
    sc = SolutionCombiner(imgCtrl, ign, coordinates=coordinates)
    valid = sc.combine(w, h, r, R)
    if valid == -1:
        return FileNotFoundError
    sc.get_surfaces()
    sc.get_confidence(loaded_model)
    return json.loads(str(sc))


@ app.post("/estimateSurface/address/fromCV", response_model=FullResponse)
def estimateSurface_coords_from_cv(req: addressRequest):
    imgCtrl = ImagesController(static_path)
    ign = IGN_API(data_path)
    sc = SolutionCombiner(imgCtrl, ign)
    sc.set_address(req.address)
    valid = sc.combine(w, h, r, R)
    if valid == -1:
        return FileNotFoundError
    sc.get_surfaces()
    sc.get_confidence(loaded_model)
    return json.loads(str(sc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
