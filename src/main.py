from common import *
from database import *
import requests
import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify

app = Flask(__name__)
app.secret_key = "y098765rtyfghjUIASDTYGHJAUISO*IUIY^&%RTFAGD"

#Erics shit 
@app.route('/AgentSend')
def AgentSend():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    un = GetUser(username)
    if un.HashedPassword != password:
        return jsonify({"error": "Incorrect username or password"}), 400
    for software in data.get('Softwares'):
        AddSoftware(username,software['Name'],software['Version'])


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

if __name__ == "__main__":
    InitDataBase()
    app.run(debug=True)
