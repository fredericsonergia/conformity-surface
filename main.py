from flask import Flask, request, Response
from flask_cors import cross_origin, CORS
from surface_estimator import estimate_surface

app = Flask(__name__)
app.config["SECRET_KEY"] = "the quick brown fox jumps over the lazy   dog"
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app, resources={
            r"/estimateSurface": {"origins": "http://localhost:8080"}})


@app.route("/estimateSurface", methods=["POST"])
@cross_origin(origin="localhost", headers=["Content-Type", "Authorization"])
def estimateSurface():

    if not request.is_json:
        return "Request was not a JSON", 400
    req = request.get_json(force=True)

    info, closestFunction, doThePlot = (
        req["info"],
        req["closestFunction"],
        req["doThePlot"],
    )
    info = getInfo(info)

    if doThePlot:
        print(doThePlot)
        if closestFunction:
            print(closestFunction)
            surface = estimate_surface(info, closestFunction, True)
        else:
            surface = estimate_surface(info, doThePlot=True)
    else:
        if closestFunction:
            print(closestFunction)
            surface = estimate_surface(info, closestFunction)
        else:
            surface = estimate_surface(info)
    response = Response(surface)
    return response


def getInfo(info):
    info = info[1:-1].split(",")
    address = info[0]
    testSurf = float(info[1])
    coordinates = info[2] + "," + info[3]
    coordinates = coordinates[1:-1].split(",")
    coordinates = (float(coordinates[0]), float(coordinates[1]))
    info = [address, testSurf, coordinates]
    return info


if __name__ == "__main__":
    app.run(debug=True)
