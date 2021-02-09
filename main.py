from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import json
import pickle
import configparser

from surface_estimator import SurfaceController
from surface_estimator.computer_vision.combine_solutions import SolutionCombiner


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

app.mount("/static", StaticFiles(directory="static"), name="static")

"""
Recover the configuration file 
"""
config = configparser.ConfigParser()
config.read("surface.config")
Image, Confidence = config['IMAGE'], config['CONFIDENCE']
w, h, r, R = int(Image["width in px"]), int(Image["height in px"]), float(
    Image["ratio in px/m"]), float(Image["Radius in m"])
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


@app.post("/estimateSurface/coordinates", response_model=BasicResponse)
def estimateSurface_coords(req: coordsRequest):

    coordinates = [float(coord) for coord in req.coordinates.split(',')]
    controller = SurfaceController()
    controller.set_coordinates(coordinates)
    controller.set_surface()
    controller.get_image(w, h)
    response = {"surface": controller.computedSurf,
                "coords": controller.image_coordinates, "fileName": controller.file_name[1:]}
    return response


@ app.post("/estimateSurface/address", response_model=BasicResponse)
def estimateSurface_address(req: addressRequest):

    address = req.address
    controller = SurfaceController()
    controller.set_address(address)
    controller.set_surface()
    controller.get_image(w, h)
    response = {"surface": controller.computedSurf,
                "coords": controller.image_coordinates, "fileName": controller.file_name[1:]}
    return response


@ app.post("/estimateSurface/coordinates/fromCV", response_model=FullResponse)
def estimateSurface_coords_from_cv(req: coordsRequest):

    coordinates = [float(coord) for coord in req.coordinates.split(',')]
    sc = SolutionCombiner(coordinates)
    valid = sc.combine(w, h, r, R)
    if valid == -1:
        return FileNotFoundError
    sc.get_surfaces()
    sc.get_confidence(loaded_model)
    return json.loads(str(sc))


@ app.post("/estimateSurface/address/fromCV", response_model=FullResponse)
def estimateSurface_coords_from_cv(req: addressRequest):
    sc = SolutionCombiner()
    sc.set_address(req.address)
    valid = sc.combine(w, h, r, R)
    if valid == -1:
        return FileNotFoundError
    sc.get_surfaces()
    sc.get_confidence(loaded_model)
    return json.loads(str(sc))
