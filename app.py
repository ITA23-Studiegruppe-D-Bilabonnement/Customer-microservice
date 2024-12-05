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
            "PATH": "/register",
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
            "PATH": "/delete/id",
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
            }
        ]
    })



# Register user endpoint - "/register"
@app.route("/register", methods=["POST"])
@swag_from("swagger/register.yaml")
def register_user():
    data = request.get_json()

    #Check to see if the user has insert all the data
    if not data or "email" not in data or "first_name" not in data or "last_name" not in data or "password" not in data:
        return jsonify({
            "Error": "Youre missing one of the following: email, first_name, last_name, password"
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
            return jsonify({
                "Message": "Successfully created user"
            }), 200
        # Handle execptions/errors
        # Null values is already checked - so we only need to handle if the email isnt unique
    except sqlite3.IntegrityError:
        return jsonify({
            "Error": "Email already in use"
        }), 400
        # Handle random errors
    except Exception as e:
        return jsonify({
            "Error": "OOPS! Something went wrong :(",
            "Message": f'{e}'
        }), 500

# Delete user endpoints - "/delete"
@app.route("/delete/<int:id>", methods=["DELETE"])
@swag_from("swagger/delete.yaml")
def delete_user(id):

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id=?", (id,))

            #Check to see if the database was affected
            if cur.rowcount == 0:
                return jsonify({
                    "Error": "Couldnt find the user"
                }), 400
            
            return jsonify({
                "message": "User deleted succesfully"
            }), 200
        #Handle random errors
    except Exception as e:
        return jsonify({
            "Error": "OOPS! Something went wrong :(",
            "Message": f'{e}'
        }), 500
        

# Login user endpoint - "/login"
@app.route("/login", methods=["POST"])
@swag_from("swagger/login.yaml")
def login_user():

    data = request.get_json()

    #Check to see if the user has insert all the data
    if not data or "email" not in data or "password" not in data:
        return jsonify({
            "Error": "Email or password is missing"
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
                jwt_token = create_access_token(identity=user[0])
                return jsonify({
                    "Message": "Login successful",
                    "JWT-Token": jwt_token
                }), 200
            
            # If the password didnt match
            return jsonify({
                "Error": "Wrong email or password"
            }), 401
        
        # Handle random errors #####
    except Exception as e:
        return jsonify({
            "Error": "OOPS! Something went wrong :(",
            "Message": f'{e}'
        }), 500
        

#ONLY TESTNING ENDPOINT - REMOVE AFTER TESTING IS DONE
# NOTES 
        #first_row = data[0]
        #print(first_row[1])
        #Just some notes on how to access specific data returned
# JUST ADDED THIS TO FORCE UPDATE ON IMAGE ( DOCKERHUB -> AZURE - CHECK IF THE DATA STAYS)

@app.route("/listofusers", methods=["GET"])
def test():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(""" SELECT email, first_name, last_name FROM users""")
        data = cur.fetchall()

        #Get the coulmns name
        columns = [description[0] for description in cur.description]

        #Format the user in json/dict format
        users = []
        for row in data:
            user = dict(zip(columns, row))  
            users.append(user)

        return jsonify({
            "message": users
        })

if __name__ == "__main__":
    app.run(debug=True)
