from flask import Flask, jsonify, request
import requests
import sqlite3
import bcrypt
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flasgger import swag_from

app = Flask(__name__)


@app.route("/")
def homepoint():
    return jsonify({"TEST: TEST"})


 
app.run(debug=True)