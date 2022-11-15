#Flying Karate Masters: Matthew Yee, Kevin Li, Joseph Wu
#SoftDev
#P00 -- Story Game
#2022-11-14
#time spent: 13.5 hours

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
    if 'username' in session:
        return app.redirect("/main")
    #both the database and the cursor need to be connected in the function it is used in because they must run in the same thread
    users_db = sqlite3.connect(USER_DB_FILE)
    users_c = users_db.cursor()
    story_db = sqlite3.connect(STORY_DB_FILE)
    story_c = story_db.cursor()
    
    users_c.execute("SELECT tbl_name FROM sqlite_master")
    if len(users_c.fetchall()) < 1:
        users_c.execute("CREATE TABLE users(username TEXT PRIMARY KEY, password TEXT)")
    story_c.execute("SELECT tbl_name FROM sqlite_master")
    if len(story_c.fetchall()) < 1:
        story_c.execute("CREATE TABLE stories(title PRIMARY KEY, full_text, latest_entry, contributors)")
    
    error = ""
    username = ""
    users_c.execute("SELECT * FROM users")
    user_list = users_c.fetchall()
    print("valid usernames are :" + str(user_list))

    #the following code will only run if the user submits the form on the login page
    if request.method == "POST":
        #diagnostic prints
        print("inputted username is " + request.form['username'])
        print("inputted password is " + request.form['password'])

        #to catch an incomplete operation exception that occurs if the username field is
        try:
            username = request.form['username']
            #inserts username as a tuple containing one item because the ? substitution requires a tuple
            #looks in the database to see if the username entered exists in the users database
            print("executing: SELECT * FROM users GROUP BY username HAVING username=?", (username,))
            users_c.execute("SELECT * FROM users GROUP BY username HAVING username=?", (username,))
        except:
            #print error message if username is not found in database
            error = "username not found"
            print("user with username: " + request.form['username'] + " was not found in database")
            return render_template('login.html', error_message = error)
        #if username is found, get the corresponding record from the database
        credentials = users_c.fetchall()
        print(f"Found the following record for user {username}: {credentials}")
        
        #since we got the record as a list of tuples, we can check the length of the list to see if the query had any matches
        #username is a primary key, so there will be at most one record
        if len(credentials) > 0:
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
    if 'username' in session:
        return app.redirect("/main")
    error=''
    if request.method == 'POST':
        #check for an empty username
        if request.form['username'].strip() == '':
            error = 'No username submitted'
            return render_template('register.html', error_message = error)
        #check for an empty password
        if request.form['password'].strip() == '':
            error = 'No password submitted'
            return render_template('register.html', error_message = error)
        #prevent whitespaces to prevent usernames and passwords like "         e"
        if ' ' in request.form['username'] or ' ' in request.form['password']:
            error = 'Whitespace is not permitted in the username or password'
            return render_template('register.html', error_message = error)

        users_db = sqlite3.connect(USER_DB_FILE)
        users_c = users_db.cursor()
        #get the record with the username entered
        username = request.form['username']
        users_c.execute("SELECT * FROM users GROUP BY username HAVING username=?", (username,))
        user_list = users_c.fetchall()
        
        #if the record / username exists
        if len(user_list) > 0:
            error = 'Username already exists'
            return render_template('register.html', error_message = error)
        else:
            password = request.form['password']
            #add the user into the user database
            command ="INSERT INTO users values(?, ?);"
            users_c.execute(command, (username, password))
            users_db.commit()
            
            #diagnostic print
            users_c.execute("SELECT * FROM users")
            user_list = users_c.fetchall()
            print(user_list)

            error = 'Account Created, Navigate to Login'
            return render_template('register.html', error_message = error)
            #confirmation message
            
    return render_template('register.html')

@app.route('/main', methods = ['GET', 'POST'])
def main():
    not_contributed = []
    contributed = []
    created = []
    not_contributed_dict = {}
    contributed_dict = {}
    created_dict = {}

    story_db = sqlite3.connect(STORY_DB_FILE)
    story_c = story_db.cursor()
    #get a list of table names
    story_c.execute("SELECT title FROM stories")
    story_list = story_c.fetchall()
    #get a list of contributors and sort stories
    for title in story_list:
        story_c.execute("SELECT contributors FROM stories WHERE title=?", title)
        contributor_list = story_c.fetchone()[0]
        creator_list = contributor_list.split(" ")

        if session['username'] == creator_list[0]: #checks if the current user has created the story being checked
            created.append(title[0])
        elif session['username'] in contributor_list: #checks if the current user has contributed to story being checked
            contributed.append(title[0])
        else:
            not_contributed.append(title[0])
    print("Contributed: " + str(contributed))
    print("Not contributed: " + str(not_contributed))

    for title in created: #uses the titles under the created list to populate a dictionary containing titles as keys and the number of contributors as definitions
        story_c.execute("SELECT contributors FROM stories WHERE title=?", (title,))
        numbers = story_c.fetchone()[0]
        number_list = numbers.split(" ")
        created_dict[title] = len(number_list)

    for title in not_contributed:
        story_c.execute("SELECT contributors FROM stories WHERE title=?", (title,))
        numbers = story_c.fetchone()[0]
        number_list = numbers.split(" ")
        not_contributed_dict[title] = len(number_list)

    for title in contributed:
        #story_list: [(ducks, ), (more ducks,), (even more ducks,)]
        story_c.execute("SELECT contributors FROM stories WHERE title=?", (title,))
        numbers = story_c.fetchone()[0] #"Kevin Matthew Joseph"
        number_list = numbers.split(" ") #["Kevin", "Matthew", "Joseph"]
        contributed_dict[title] = len(number_list)

    try:
        return render_template('main.html', username=session['username'], not_contributed_dict = not_contributed_dict, contributed_dict = contributed_dict, created_dict = created_dict)
    except:
        return app.redirect(app.url_for('login'))

@app.route('/create', methods = ['GET', 'POST'])
def makeStory():
    if not 'username' in session:
        return app.redirect("/")
    if request.method == 'POST':
        stories_db = sqlite3.connect(STORY_DB_FILE)
        stories_c = stories_db.cursor()
        
        title = request.form['title']
        contents = request.form['contents']
        username = session['username']
        list_of_errors = []

        #all expected errors
        stories_c.execute("SELECT title FROM stories")
        list_of_titles = stories_c.fetchall()
        if (title,) in list_of_titles: #duplicate title
            list_of_errors.append("a story with that name already exists")
        if (title.strip() == ''): #no title
            list_of_errors.append("your story needs a title")
        if (contents.strip() == ''): #no contents
            list_of_errors.append("your story needs some starting lines")
        if len(list_of_errors) > 0:
            return render_template('new_story.html', error_message = list_of_errors)

        try:
            stories_c.execute("INSERT INTO stories VALUES (?, ?, ?, ?)", (title, contents, contents, username))
            stories_db.commit()
        except:
            return render_template('new_story.html', message = "an unexpected error has occurred, please try with a different title and / or text")
        
        stories_c.execute("SELECT title FROM stories")
        print(stories_c.fetchall())
        response = 'Story created, navigate to the home page to see all your stories.'
        return render_template('new_story.html', message = response)
    return render_template('new_story.html')

@app.route('/edit', methods = ['GET', 'POST'])
def edit():
    if request.method == "POST":
        stories_db = sqlite3.connect(STORY_DB_FILE)
        stories_c = stories_db.cursor()

        title = request.form['title']
        print("The title of the story is: " + title)
        stories_c.execute("SELECT latest_entry FROM stories WHERE title=?", (title,))
        previous_entry = stories_c.fetchone()[0]

        error = ""

        stories_c.execute("SELECT contributors FROM stories WHERE title=?", (title,))
        contributor_list = stories_c.fetchone()[0]
        contributors = contributor_list
        contributor_list = contributor_list.split(" ")
        
        stories_c.execute("SELECT full_text FROM stories WHERE title=?", (title,))
        full_text = stories_c.fetchone()[0]

        if session['username'] in contributor_list:
            full_text = full_text.split("<br>")
            return render_template('full_story.html', story_title = title, full_story = full_text)
                

        if 'contents' in request.form:
            #prevent users from adding this split key into the contents
            if "<br>" in request.form['contents']:
                return render_template('edit.html', story_title = title, latest_entry = previous_entry, error_message = error)

            full_text += "<br>" + request.form['contents'] 
            contributors += " " + session['username']

            stories_c.execute("UPDATE stories SET full_text=?, latest_entry=?, contributors=? WHERE title=?",(full_text, request.form['contents'], contributors, title))
            stories_db.commit()

            full_text = full_text.split("<br>")

            stories_c.execute("SELECT * FROM stories WHERE title=?", (title,))
            print(stories_c.fetchone())
            return render_template('full_story.html', story_title = title, full_story = full_text)

    return render_template('edit.html', story_title = title, latest_entry = previous_entry)


@app.route('/search', methods = ['GET', 'POST'])
def search():
    search_dict = {}
    
    if request.method == "POST":
        story_db = sqlite3.connect(STORY_DB_FILE)
        story_c = story_db.cursor()
        story_c.execute("SELECT title FROM stories")
        story_list = story_c.fetchall()
        error = ""

        search_results = []

        #story_list is a tuple list
        for title in story_list:
            if request.form['find'].lower() in title[0].lower():
                search_results.append(title[0])
        
        #running through the newly created string list to find # of entries pertaining to each result
        #result and numbers added to dict
        for title in search_results:
            story_c.execute("SELECT contributors FROM stories WHERE title=?", (title,))
            numbers = story_c.fetchone()[0]
            number_list = numbers.split(" ")
            search_dict[title] = len(number_list)

        if len(search_results) == 0:
            error = f"No results found for '{request.form['find']}'"

        return render_template('search.html', search = request.form['find'], search_dict = search_dict, error_message = error)

        


if __name__ == "__main__": #false if this file imported as module
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
