from flask import Flask
from flask import request
from surface_estimator import estimate_surface

app = Flask(__name__)


@app.route("/estimateSurface", methods=["POST"])
def estimateSurface():
    info, closestFunction, doThePlot = (
        request.form["info"],
        request.form["closestFunction"],
        request.form["doThePlot"],
    )
    if doThePlot:
        return estimate_surface(info, closestFunction, True)
    else:
        return estimate_surface(info, closestFunction)
