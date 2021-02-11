from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from functools import lru_cache

import json
import pickle
import configparser

import sys

sys.path.append('../')

import app.config as config
from surface_estimator import SurfaceController
from surface_estimator.computer_vision.combine_solutions import SolutionCombiner
import uvicorn
from surface_estimator.getImage import ImagesController
from surface_estimator.IGN_API import IGN_API


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
# config = configparser.ConfigParser()
# config.read("app.config")
# Image, Confidence, Data = config['IMAGE'], config['CONFIDENCE'], config["DATA"]
# w, h, r, R = int(Image["width in px"]), int(Image["height in px"]), float(
#     Image["ratio in px/m"]), float(Image["Radius in m"])
# data_path, static_path = Data["data_path"], Data["static_path"]
# model_path = Confidence["model_path"]
# loaded_model = pickle.load(open(Confidence["model_path"], 'rb'))


@lru_cache()
def get_settings():
    config = configparser.ConfigParser()
    config.read("app.config")
    Image, Confidence, Data = config['IMAGE'], config['CONFIDENCE'], config["DATA"]
    w, h, r, R = int(Image["width in px"]), int(Image["height in px"]), float(
        Image["ratio in px/m"]), float(Image["Radius in m"])
    data_path, static_path = Data["data_path"], Data["static_path"]
    model_path = Confidence["model_path"]
    loaded_model = pickle.load(open(Confidence["model_path"], 'rb'))
    return config.Settings(w=w, h=h, r=r, R=R, data_path=data_path, static_path=static_path, loaded_model=loaded_model)


# if __name__=="__main__":
#     c = Config("app.config")
#     app.mount("/static", StaticFiles(directory=c.static_path), name="static")

# class Config():
#     def __init__(self, config_file):
#         config = configparser.ConfigParser()
#         config.read(config_file)
#         Image, Confidence, Data = config['IMAGE'], config['CONFIDENCE'], config["DATA"]
#         self.w, self.h, self.r, self.R = int(Image["width in px"]), int(Image["height in px"]), float(
#             Image["ratio in px/m"]), float(Image["Radius in m"])
#         self.data_path, self.static_path = Data["data_path"], Data["static_path"]
#         self.loaded_model = pickle.load(open(Confidence["model_path"], 'rb'))
#     def get_app(self):
#         return app

"""
Define the data classes
"""


class coordsRequest(BaseModel):
    coordinates: str = "4.223243,49.232043"


class addressRequest(BaseModel):
    address: str = "20 rue de la paix, 78190"


class BasicResponse(BaseModel):
    surface: float = 120
    coords: list = [4.223243,49.232043]
    fileName: str = "/static/4.223243,49.232043/1.png"


class FullResponse(BaseModel):
    surface: float = 120
    coords: list = [4.223243,49.232043]
    fileName: str = "/static/4.223243,49.232043/1.png"
    contours: list = [[[0,0], [1,1], [1,0]], [[[0,0], [2,1], [1,0]]]]
    surfaces: list = [120, 12]
    metrics: list = [{"label": "TAU", "value": 12}, {"label": "conf", "value": 0}]


"""
Define the routes
"""



@app.post("/surface/coordinates", response_model=BasicResponse)
def estimateSurface_coords(req: coordsRequest, settings: config.Settings = Depends(get_settings)):
    print(req.coordinates)
    coordinates = [float(coord) for coord in req.coordinates.split(',')]
    imgCtrl = ImagesController(settings.static_path)
    ign = IGN_API(settings.data_path)
    controller = SurfaceController(imgCtrl, ign)
    controller.set_coordinates(coordinates)
    controller.set_surface()
    controller.get_image(settings.w, settings.h)
    response = BasicResponse(surface=controller.computedSurf,
                            coords=controller.image_coordinates, 
                            filename=controller.file_name[2:])
    return response


@ app.post("/surface/address", response_model=BasicResponse)
def estimateSurface_address(req: addressRequest, settings: config.Settings = Depends(get_settings)):

    address = req.address
    imgCtrl = ImagesController(settings.static_path)
    ign = IGN_API(settings.data_path)
    controller = SurfaceController(imgCtrl, ign)
    controller.set_address(address)
    controller.set_surface()
    controller.get_image(settings.w, settings.h)
    response = BasicResponse(surface=controller.computedSurf,
                            coords=controller.image_coordinates, 
                            filename=controller.file_name[2:])
    return response


@ app.post("/surface/coordinates/fromCV", response_model=FullResponse)
def estimateSurface_coords_from_cv(req: coordsRequest, settings: config.Settings = Depends(get_settings)):

    coordinates = [float(coord) for coord in req.coordinates.split(',')]
    imgCtrl = ImagesController(settings.static_path)
    ign = IGN_API(settings.data_path)
    sc = SolutionCombiner(imgCtrl, ign, coordinates=coordinates)
    valid = sc.combine(settings.w, settings.h, settings.r, settings.R)
    if valid == -1:
        return FileNotFoundError
    sc.get_surfaces()
    sc.get_confidence(settings.loaded_model)
    return json.loads(str(sc))


@ app.post("/surface/address/fromCV", response_model=FullResponse)
def estimateSurface_coords_from_cv(req: addressRequest, settings: config.Settings = Depends(get_settings)):
    imgCtrl = ImagesController(settings.static_path)
    ign = IGN_API(settings.data_path)
    sc = SolutionCombiner(imgCtrl, ign)
    sc.set_address(req.address)
    valid = sc.combine(settings.w, settings.h, settings.r, settings.R)
    if valid == -1:
        return FileNotFoundError
    sc.get_surfaces()
    sc.get_confidence(settings.loaded_model)
    return json.loads(str(sc))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
