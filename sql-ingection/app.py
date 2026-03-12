from flask import Flask, request, jsonify
import sqlite3

app =  Flask(__name__)

@app.route('/login')
def login():

    username = request.args.get['username']
    password = request.args.get['password']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    query = f" SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print("Executing query: ", query)
    cur.execute(query)
    result = cur.fetchone()
    if result:
        return "Login success"
    else: 
        return "Login failed"

app.run(debug=True)