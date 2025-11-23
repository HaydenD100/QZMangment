from common import *
from enrichment import *

from database import *
import requests
import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.secret_key = "y098765rtyfghjUIASDTYGHJAUISO*IUIY^&%RTFAGD"
@app.route('/')
def default_route():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        un = GetUser(username)
        if un == None:
            return render_template("login.html", error="Invalid username or password")
        elif un.HashedPassword == password:
            return redirect(url_for('dashboard', user=username, pwd=password))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    username = request.args.get("user")
    pwd = request.args.get("pwd")

    # Missing either → deny
    if not username or not pwd:
        return redirect(url_for('login'))

    # User invalid → deny
    if GetUser(username) == None:
        return redirect(url_for('login'))

    # Password mismatch → deny
    if GetUser(username).HashedPassword != pwd:
        return redirect(url_for('login'))

    # All checks passed
    return f"Welcome, {username}!"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



#Erics shit 
@app.route('/AgentSend', methods=['POST'])
def AgentSend():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()

    # Parse authentication info from nested JSON
    auth = data.get("auth", {})
    username = auth.get("username")
    password = auth.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Authenticate user
    un = GetUser(username)
    if un.HashedPassword != password:
        return jsonify({"error": "Incorrect username or password"}), 400

    # Parse installed software list
    softwares = data.get("installed_software", [])
    for software in softwares:
        name = software.get("name")
        version = software.get("version")
        if name and version:
            AddSoftware(username, name, version)

    return jsonify({"status": "success"}), 200

@app.route('/GetUser', methods=['GET', 'POST'])
def get_user_info():
    if request.method == "GET":
        username = request.args.get("username")
        password = request.args.get("password")
    else:  # POST
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

    # Validate input
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Get user from database
    un = GetUser(username)
    if not un:
        return jsonify({"error": "User not found"}), 404

    # Check password
    if un.HashedPassword != password:
        return jsonify({"error": "Incorrect username or password"}), 400
    # Return user info
    return  serialize_user(GetUser(username))
    
#getting software belonging to user GetSoftwareByUser()
@app.route('/GetUserSoftware', methods=['POST'])
def GetUserSoftware():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    un = GetUser(username)
    if not un:
        return jsonify({"error": "User not found"}), 404
    if un.HashedPassword != password:
        return jsonify({"error": "Incorrect username or password"}), 400
    if(username == "admin@qz.com"):
        software_list = GetAllSoftware()
    else:
        software_list = GetSoftwareByUser(username)
        
    json_list = [serialize_software(sw) for sw in software_list]
    return jsonify(json_list) 

@app.route('/GetSoftwareByName', methods=['POST'])
def GetSoftwareByName():
    try:
        data = request.get_json()
        print("Received:", data)

        if not data:
            return jsonify({"error": "JSON body required"}), 400

        # Match what your frontend sends
        name = data.get("softwareName")
        print(name)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        # Get the Software object
        print("ID" + str(name))
        software = GetSoftwareByID(name)
        if not software:
            return jsonify({"error": "Software not found"}), 404
        # Return JSON properly
        return jsonify(serialize_software(software))

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/GetSoftware', methods=['GET'])
def GetSoftware():
    username = request.args.get("username")
    software = request.args.get("software")

    password = request.args.get("password")
    data = request.get_json()
    sftwbu = GetSoftwareByUser(username,software)
    return jsonify(sftwbu)
    
@app.route('/AddSoftware', methods=['GET'])
def AddSoftwareDB():
    data = request.get_json()
    username = data.get('UserName')
    name = data.get('Name')
    version = data.get('Version')
    AddSoftware(username,name,version)

if __name__ == "__main__":
    InitDataBase()
    #EnrichData()
    app.run(debug=True)
    