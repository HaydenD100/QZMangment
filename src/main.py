from common import User
import requests
import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "y098765rtyfghjUIASDTYGHJAUISO*IUIY^&%RTFAGD"
user_list = [User(123, "admin", "pass")]
credentials = {user.Name: user.HashedPassword for user in user_list}

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

        # validate plain-text credentials
        if username in credentials and credentials[username] == password:
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
    if username not in credentials:
        return redirect(url_for('login'))

    # Password mismatch → deny
    if credentials[username] != pwd:
        return redirect(url_for('login'))

    # All checks passed
    return f"Welcome, {username}!"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)