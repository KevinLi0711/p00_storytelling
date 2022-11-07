#Flying Karate Masters: Matthew Yee, Kevin Li, Joseph Wu
#SoftDev
#K19 -- Cookies
#2022-11-03
#time spent: 0.2 hours

from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session

import sqlite3s



app = Flask(__name__)    #create Flask object

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

username = 'karate'
password = '1234'

'''
@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return app.redirect(app.url_for('login'))
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""
    form_keys = request.form.keys()
    print(request.form)

    #Only assign values to session is there are values in request.form to prevent a key error
    if 'username' in request.form and 'password' in request.form:
        session['username'] = request.form['username']
        session['password'] = request.form['password']

    #Checks if the username and password are in session to prevent a key error
    if 'username' in session and 'password' in session:
        #Check if the username and password in session match the hardcoded values
        if session['username'] == username and session['password'] == password:
            return render_template('response.html', username = session['username'])

        #print an error message on the bottom of the login page depending on what was wrong
        if not session['password'] == password:
            error = "incorrect password"
        if not session['username'] == username:
            error = "username not found"
    
    return render_template('login.html', error_message = error)

@app.route('/logout', methods=["GET", "POST"])
def logout():
    #Checks if there is a username and password in session before popping to prevent a key error
    if 'username' in session and 'password' in session:
        session.pop('username') #removes the username from the session
        session.pop('password') #removes the password from the session
    #print(session.__dict__)
    #print(session.keys)
    return app.redirect(app.url_for('login')) #Sends the user back to the login page


if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
