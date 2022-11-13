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
STORY_DB_FILE = "story.db"

@app.route('/', methods=['GET', 'POST'])
def login():
    #both the database and the cursor need to be connected in the function it is used in because they must run in the same thread
    users_db = sqlite3.connect(USER_DB_FILE)
    users_c = users_db.cursor()
    error = ""
    username = ""
    users_c.execute(f"SELECT * FROM users")
    user_list = users_c.fetchall()
    print(user_list)

    if 'username' in request.form:
        print("inputted username is " + request.form['username'])
        print("inputted password is " + request.form['password'])

        #to catch an incomplete operation exception that occurs if the user inputs nothing into the form
        try:
            username = request.form['username']
            #inserts username as a tuple containing one item because the ? substitution requires a tuple
            print("executing: SELECT * FROM users GROUP BY username HAVING username=?", (username,))
            users_c.execute("SELECT * FROM users GROUP BY username HAVING username=?", (username,))
        except:
            error = "username not found"
            print("user with username: " + request.form['username'] + " was not found in database")
            return render_template('login.html', error_message = error)

        credentials = users_c.fetchall()
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
                return app.redirect(app.url_for('main'))
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
    return app.redirect(app.url_for('login')) #Sends the user back to the login page

@app.route('/goingbacktologin', methods=["GET", "POST"])
def tologin():
    return app.redirect(app.url_for('login')) #Sends the user back to the login page

@app.route('/register', methods=["GET", "POST"])
def register():
    error=''
    if request.method == 'POST':

        if request.form['username'] == '':
            error = 'No username submitted'
            return render_template('register.html', error_message = error)

        if request.form['password'] == '':
            error = 'No password submitted'
            return render_template('register.html', error_message = error)

        if ' ' in request.form['username'] or ' ' in request.form['password']:
            error = 'Whitespace is not permitted in the username or password'
            return render_template('register.html', error_message = error)

        users_db = sqlite3.connect(USER_DB_FILE)
        users_c = users_db.cursor()
        username = request.form['username']
        users_c.execute("SELECT * FROM users GROUP BY username HAVING username=?", (username,))
        user_list = users_c.fetchall()
        
        #username already exists
        if len(user_list) > 0:
            error = 'Username already exists'
            return render_template('register.html', error_message = error)
        else:
            password = request.form['password']
            command ="INSERT INTO users values(?, ?);"
            users_c.execute(command, (username, password))
            users_db.commit()
            
            users_c.execute("SELECT * FROM users")
            user_list = users_c.fetchall()
            print(user_list)
            error = 'Account Created, Navigate to Login'
            return render_template('register.html', error_message = error)
            #confirmation message
            
    return render_template('register.html')

@app.route('/main', methods = ['GET', 'POST'])
def main():
    stories_available = ''

    story_db = sqlite3.connect(STORY_DB_FILE)
    story_c = story_db.cursor()
    story_c.execute("SELECT tbl_name FROM sqlite_schema")
    story_list = story_c.fetchall()

    for i in story_list:
        for a in i:
            stories_available += a+'<br>'
    
    try:
        return render_template('main.html', username=session['username'], stories = stories_available)
    except:
        return app.redirect(app.url_for('login'))

@app.route('/create', methods = ['GET', 'POST'])
def makeStory():
    if request.method == 'POST':
        stories_db = sqlite3.connect(STORY_DB_FILE)
        stories_c = stories_db.cursor()
        
        title = request.form['title']
        contents = request.form['contents']
        username = session['username']
        list_of_errors = []

        try:
            command = "CREATE TABLE '?' (Entry, Username);"
            stories_c.execute(command, (title,))
        except:
            if (title.strip() == ''):
                list_of_errors.append("your story needs a title")
            if (contents.strip() == ''):
                list_of_errors.append("your story needs some starting lines")
            #currently doesn't work
            stories_c.execute("SELECT tbl_name FROM sqlite_schema")
            list_of_titles = stories_c.fetchall()
            title = (title,)
            print("Title exists: " + str(title in list_of_titles))
            if title in list_of_titles:
                list_of_errors.append("a story with that name already exists")
            return render_template('new_story.html', error_message = list_of_errors)

        command = "INSERT INTO '?' values('?','?');"
        stories_c.execute(command, (title, contents, username))
        stories_db.commit()

        print(list_of_titles)
        error = 'Story created, navigate to the home page to see all your stories.'
        return render_template('new_story.html', error_message = error)
    return render_template('new_story.html')
if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
