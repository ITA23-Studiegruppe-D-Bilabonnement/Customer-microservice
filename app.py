from flask import Flask, jsonify, request
import requests
import sqlite3
import bcrypt
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flasgger import swag_from
from swagger.swagger_config import init_swagger

app = Flask(__name__)

#Load the enviroment variables
load_dotenv()

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
DB_PATH = os.getenv('SQLITE_DB_PATH')
PORT = int(os.getenv('PORT', 5000))
jwt = JWTManager(app)

# Initialize Swagger
init_swagger(app)


#Database creation
def initialize_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS users
                    (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    password text NOT NULL
                    )""")
        conn.commit()
        
initialize_db()

#Homepoint - "/"
@app.route("/", methods=["GET"])
def homepoint():
    return jsonify({
        "SERVICE": "CUSTOMER MICROSERVICE",
        "AVAILABLE ENDPOINTS": [
            {
            "PATH": "/user",
            "METHOD": "POST",
            "DESCRIPTION": "Registers new user in the database",
            "BODY": {
                "email": "STRING",
                "first_name": "STRING",
                "last_name": "STRING",
                "password": "STRING"
                }
            },
            {
            "PATH": "/user/id",
            "METHOD": "DELETE",
            "DESCRIPTION": "Deletes user from database",
            "PARAMETER": "id"
            },
            {
            "PATH": "/login",
            "METHOD": "POST",
            "DESCRIPTION": "Login user",
            "BODY": {
                "email": "STRING",
                "password": "STRING"
            }
            },
            {
                "PATH": "/user",
                "METHOD": "GET",
                "DESCRIPTION": "Returns user information (first and last name) based on JWT-token(id) ",
                "AUTHORIZATION": {
                    "REQUIRED": "Yes",
                    "TYPE": "JWT token"
                }
            },
            {
                "PATH": "/user/id",
                "METHOD": "GET",
                "DESCRIPTION": "Returns user information based on search by id ",
                "PARAMETER": "id"
            }
        ]
    }), 200

# Register user endpoint - "/user" METHOD(POST)
@app.route("/user", methods=["POST"])
@swag_from("swagger/register.yaml")
def register_user():
    data = request.get_json()

    #Check to see if the user has inserted all the data
    required_fields = ["email","first_name","last_name","password"]
    for field in required_fields:
        if not data or field not in data or not data[field]:
            return jsonify({
                "error": f"Youre missing the {field} field"
            }), 400
        
    email = data["email"]
    first_name = data["first_name"]
    last_name = data["last_name"]
    password = data["password"]

    #Crypt password
    crypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    #Insert into the database
    try: 
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(""" INSERT INTO users
                        (
                        email,
                        first_name,
                        last_name,
                        password
                        ) VALUES(?,?,?,?)""", (email, first_name, last_name, crypted_password))
            conn.commit()
            #User created successfully
            return jsonify({
                "message": "Successfully created user"
            }), 200
        # Handle execptions/errors
        # Null values is already checked - so we only need to handle if the email isnt unique
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Email already in use"
        }), 400
        # Handle random errors
    except Exception as e:
        return jsonify({
            "error": "OOPS! Something went wrong :(",
            "message": f'{e}'
        }), 500

# Delete user endpoints - "/user/id" METHOD(DELETE)
@app.route("/user/<int:id>", methods=["DELETE"])
@swag_from("swagger/delete.yaml")
def delete_user(id):

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id=?", (id,))

            #Check to see if the database was affected
            if cur.rowcount == 0:
                return jsonify({
                    "error": "Couldnt find the user"
                }), 400
            #User deleted successfully
            return jsonify({
                "message": "User deleted succesfully"
            }), 200
        #Handle random errors
    except Exception as e:
        return jsonify({
            "error": "OOPS! Something went wrong :(",
            "message": f'{e}'
        }), 500
        

# Login user endpoint - "/login" METHOD(POST)
@app.route("/login", methods=["POST"])
@swag_from("swagger/login.yaml")
def login_user():

    data = request.get_json()

    #Check to see if the user has insert all the data
    if not data or "email" not in data or "password" not in data:
        return jsonify({
            "error": "Email or password is missing"
        }), 400
    
    email = data["email"]
    password = data["password"]

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, password FROM users WHERE email = ?", (email,))
            user = cur.fetchone()

            #Check to see if the password matches
            if user and bcrypt.checkpw(password.encode('utf-8'), user[1]):
                print(str(user[0]))
                jwt_token = create_access_token(identity=str(user[0]))
                #Login successfull
                return jsonify({
                    "message": "Login successful",
                    "authorization": jwt_token
                }), 200
            
            # If the password didnt match
            return jsonify({
                "error": "Wrong email or password"
            }), 401
         
        # Handle random errors 
    except Exception as e:
        return jsonify({
            "error": "OOPS! Something went wrong :(",
            "message": f'{e}'
        }), 500
        
# Retrieve user information endpoint - "/user" - GET - ENDPOINT FOR USERS
@app.route("/user", methods=["GET"])
@jwt_required()
@swag_from("swagger/user_information.yaml")
def user_information(): 
    try:
        current_userid = get_jwt_identity()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?",(current_userid,))
            data = cursor.fetchone()

            #Check to see if it found the user
            if not data:
                return jsonify({
                    "error": "Couldnt find the user"
                }), 404
            
            return jsonify({
                "first_name": data[0],
                "last_name": data[1]
            }), 200

        # Handle random errors #####
    except Exception as e:
        return jsonify({
            "error": "OOPS! Something went wrong :(",
            "message": f'{e}'
        }), 500

@app.route("/user/<int:id>", methods=["GET"])
def user_information_search(id):

    try:
        current_userid = id
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT first_name, last_name FROM users WHERE id = ?",(current_userid,))
            data = cursor.fetchone()

            #Check to see if it found the user
            if not data:
                return jsonify({
                    "error": "Couldnt find the user"
                }), 404

            return jsonify({
                "first_name": data[0],
                "last_name": data[1]
            }), 200

        # Handle random errors 
    except Exception as e:
        return jsonify({
            "error": "OOPS! Something went wrong :(",
            "message": f'{e}'
        }), 500
        
if __name__ == "__main__":
    app.run(debug=True)
