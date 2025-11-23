from common import *
from database import *
import requests
import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from flask_cors import CORS

app = Flask(__name__)
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

if __name__ == "__main__":
    InitDataBase()

    app.run(debug=True)
    

#Erics shit
@app.route('/AgentSend', methods=['POST'])
def AgentSend():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Extract auth info
    auth = data.get('auth', {})
    username = auth.get('username')
    password = auth.get('password')
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # Validate user
    un = GetUser(username)
    if un.HashedPassword != password:
        return jsonify({"error": "Incorrect username or password"}), 400

    # Extract and add installed software
    installed_software = data.get('installed_software', [])
    for software in installed_software:
        # Use correct keys as in JSON
        name = software.get('name')
        version = software.get('version')
        if name and version:
            AddSoftware(username, name, version)

    return jsonify({"status": "success", "software_added": len(installed_software)})



@app.route('/GetUser', methods=['GET'])
def GetUserInfo():
    username = request.args.get("username")
    password = request.args.get("password")
    data = request.get_json()
    un = GetUser(username)
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    elif un.HashedPassword != password:
        return jsonify({"error": "Incorrect username or password"}), 400
    else:
        return  jsonify(GetUser(username))
    
#getting software belonging to user GetSoftwareByUser()
@app.route('/GetAllSoftware', methods=['GET'])
def GetSoftware():
    username = request.args.get("username")
    password = request.args.get("password")
    data = request.get_json()
    sftwbu = GetSoftwareByUser(username)
    return jsonify(sftwbu)
    
@app.route('/AddSoftware', methods=['GET'])
def GetUserInfo():
    data = request.get_json()
    username = data.get('UserName')
    name = data.get('Name')
    version = data.get('Version')
    AddSoftware(username,name,version)


