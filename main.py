from flask import Flask, request, Response
from flask_cors import cross_origin, CORS
from surface_estimator import SurfaceController

app = Flask(__name__)
app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy   dog"
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app, resources={
            r"/estimateSurface/coordinates": {"origins": "http://localhost:8080"}})


@app.route("/estimateSurface/coordinates", methods=["POST"])
@cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
def estimateSurface_coords():
    if not request.is_json:
        return "Request was not a JSON", 400
    req = request.get_json(force=True)
    coordinates = [float(coord) for coord in req["coordinates"].split(',')]
    w, h = 800, 400
    controller = SurfaceController()
    controller.set_coordinates(coordinates)
    controller.set_surface()
    controller.get_image(w, h)
    response = [controller.computedSurf, controller.image_coordinates]
    return Response(str(response))


@ app.route("/estimateSurface/address", methods=["POST"])
@ cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
def estimateSurface_address():
    if not request.is_json:
        return "Request was not a JSON", 400
    req = request.get_json(force=True)
    address = req["address"]
    w, h = 800, 400
    controller = SurfaceController()
    controller.set_address(address)
    controller.set_surface()
    controller.get_image(w, h)
    response = [controller.computedSurf, controller.image_coordinates]
    return Response(str(response))


if __name__ == "__main__":
    app.run(debug=True)
