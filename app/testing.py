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
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

USER_DB_FILE = "users.db"
user_db = sqlite3.connect(USER_DB_FILE)
user_c = user_db.cursor()

STORY_DB_FILE = "story.db"
story_db = sqlite3.connect(STORY_DB_FILE)
story_c = story_db.cursor()

#to get contents of a database as a list:
user_c.execute("SELECT * FROM users")
credentials = user_c.fetchall()
print("List of Credentials")
print("===================")
print(credentials)
print("===================" + "\n")

#to get a record from a database matching a certain criteria
user_c.execute("SELECT * FROM users GROUP BY username HAVING username='karate'")
karate_credentials = user_c.fetchall()
print("Karate Credentials")
print("===================")
print(karate_credentials)
print("===================" + "\n")

#to check if a piece of data exists
user_c.execute("SELECT * FROM users")
credentials = user_c.fetchall()
for record in credentials:
    if "Kevin" in record:
        print("Kevin is found")

#to get a record from a database matching a certain criteria
user_c.execute("SELECT * FROM users GROUP BY username HAVING username='karate'")
karate_credentials = user_c.fetchall()
print("Karate Credentials")
print("===================")
print("username is " + karate_credentials[0][0])
print("password is " + karate_credentials[0][1])
print("===================" + "\n")

#to get a list of tables
story_c.execute("SELECT tbl_name FROM sqlite_schema")
list_of_tables = story_c.fetchall()
print("List of tables")
print("===================")
print(list_of_tables)
print("===================" + "\n")



'''
@app.route('/', methods=['GET', 'POST'])
def login():
    #both the database and the cursor need to be connected in the function it is used in because they must run in the same thread
    user_db = sqlite3.connect(USER_DB_FILE)
    user_c = user_db.cursor()
    error = ""
    username = ""

    if 'username' in request.form:
        print("inputted username is " + request.form['username'])
        print("inputted password is " + request.form['password'])

        #to catch an incomplete operation exception that occurs if the user inputs nothing into the form
        try:
            username = request.form['username']
            print(f"executing: SELECT * FROM users GROUP BY username HAVING username='{username}'")
            user_c.execute(f"SELECT * FROM users GROUP BY username HAVING username='{username}'")
        except:
            error = "username not found"
            print("user with username: " + request.form['username'] + " was not found in database")
            return render_template('login.html', error_message = error)

        credentials = user_c.fetchall()
        print(f"Found the following record for user {username}: {credentials}")
        #fetchall() in the line above returns a list of all records in which the username matches the query, 
        #but since usernames must be unique, fetchall() will return at most 1 element
        if len(credentials) > 0:
            #credentials looks like [(password, username)]
            username = credentials[0][0]
            password = credentials[0][1]

            if request.form['password'] == password:
                #if password is correct, let the user login with that username
                session['username'] = username
                return render_template('response.html')
            else:
                error = "incorrect password"
        else:
            error = "username not found"

    return render_template('login.html', error_message = error)

@app.route('/logout', methods=["GET", "POST"])
def logout():
    #Checks if there is a username and password in session before popping to prevent a key error
    if 'username' in session:
        print("attempting to pop username")
        session.pop('username') #removes the username from the session
    #print(session.__dict__)
    #print(session.keys)
    return app.redirect(app.url_for('login')) #Sends the user back to the login page

if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
'''
