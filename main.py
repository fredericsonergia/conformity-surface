from flask import Flask, request, Response
from flask_cors import cross_origin, CORS
from surface_estimator import SurfaceController
from surface_estimator.computer_vision.combine_solutions import SolutionCombiner
import pickle
import configparser

app = Flask(__name__)
app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy   dog"
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app, resources={
            r"/estimateSurface/coordinates": {"origins": "http://localhost:8080"}})

config = configparser.ConfigParser()
config.read("surface.config")
Image, Batch, Model = config['IMAGE'], config['BATCH'], config['MODEL']
w, h, r, R = int(Image["width (px)"]), int(Image["height (px)"]), float(Image["ratio (px/m)"]), float(Image["Radius (m)"])
input_file, output_file = Batch["input"], Batch["output"]
loaded_model = pickle.load(open(Model["path"], 'rb'))

@app.route("/estimateSurface/coordinates", methods=["POST"])
@cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
def estimateSurface_coords():
    if not request.is_json:
        return "Request was not a JSON", 400
    req = request.get_json(force=True)
    coordinates = [float(coord) for coord in req["coordinates"].split(',')]
    controller = SurfaceController()
    controller.set_coordinates(coordinates)
    controller.set_surface()
    controller.get_image(w, h)
    response = {"surface": controller.computedSurf,
                "coords": controller.image_coordinates, "fileName": controller.file_name[1:]}
    return Response(str(response).replace("'", "\""))


@ app.route("/estimateSurface/address", methods=["POST"])
@ cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
def estimateSurface_address():
    if not request.is_json:
        return "Request was not a JSON", 400
    req = request.get_json(force=True)
    address = req["address"]
    controller = SurfaceController()
    controller.set_address(address)
    controller.set_surface()
    controller.get_image(w, h)
    response = {"surface": controller.computedSurf,
                "coords": controller.image_coordinates, "fileName": controller.file_name[1:]}
    return Response(str(response).replace("'", "\""))


@ app.route("/estimateSurface/coordinates/fromCV", methods=["POST"])
@ cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
def estimateSurface_coords_from_cv():
    if not request.is_json:
        return "Request was not a JSON", 400
    req = request.get_json(force=True)
    coordinates = [float(coord) for coord in req["coordinates"].split(',')]
    sc = SolutionCombiner(coordinates)
    valid = sc.combine(w, h, r, R)
    if valid == -1:
        return Response(FileNotFoundError)
    sc.get_surfaces()
    sc.get_confidence(loaded_model)
    return Response(str(sc))


if __name__ == "__main__":
    app.run(debug=True)
