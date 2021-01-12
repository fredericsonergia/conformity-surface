from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/findSurface',method='POST')
def findSurface():
    address, date =request.form['address'],request.form['date']
    return address + date