#Flying Karate Masters: Matthew Yee, Kevin Li, Joseph Wu
#SoftDev
#K19 -- Cookies
#2022-11-03
#time spent: 0.2 hours

from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session
import sqlite3

app = Flask(__name__)    #create Flask object
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'v9y$B&E)H+MbQeThWmZq4t7w!z%C*F-J'

USER_DB_FILE = "users.db"
user_db = sqlite3.connect(USER_DB_FILE)
user_c = user_db.cursor()

STORY_DB_FILE = "story.db"
story_db = sqlite3.connect(STORY_DB_FILE)
story_c = story_db.cursor()

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""

    #Only assign values to session is there are values in request.form to prevent a key error
    if 'username' in request.form and 'password' in request.form:
        session['username'] = request.form['username']
        session['password'] = request.form['password']

    #Checks if the username and password are in session to prevent a key error
    if 'username' in session and 'password' in session:
        #Check if the username and password in session match a record in the database
        user_c.execute("SELECT * FROM users GROUP BY username HAVING username=" + session['username'])
        credentials = user_c.fetchall()
        #fetchall() in the line above returns a list of all records in which the username matches the query, 
        #but since usernames must be unique, fetchall() will return at most 1 element

        #credentials looks like [(password, username)]
        username = credentials[0][0]
        password = credentials[0][1]

        if session['username'] == username and session['password'] == password:
            return render_template('response.html', username = session['username'])

        #print an error message on the bottom of the login page depending on what was wrong
        if not session['password'] == password:
            error = "incorrect password"
        if not session['username'] == username:
            error = "username not found"
    
    #might send user to the register page if they access it by typing in the URLy
    if error=='':
        return render_template('register.html')
    
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

'''
@app.route('/register', methods=["GET", "POST"])
def register():
    error=''

    #Change this to if username already exists in data base
    if 'username' == 'hi':
        error = 'Username already exists'
        return render_template('register.html', error_message = error)
    
    else:
        #add username and password into data base
    
    if error=='':
        return app.redirect(app.url_for('login')) #Sends the user back to the login page
'''

if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
