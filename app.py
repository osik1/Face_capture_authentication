from capture import detect_face, gen_frames, camera
from pydoc import pager
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re





#instatiate flask app  
app = Flask(__name__)


app.secret_key = 'your secret key'


# CONNECT APP TO DATABASE
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'face_capture'

mysql = MySQL(app)




@app.route('/')
# LOGIN FUNCTION
@app.route('/login', methods =['GET', 'POST']) 
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
		user = cursor.fetchone()
		if user:
			session['loggedin'] = True
			session['id'] = user['id']
			session['username'] = user['username']
			msg = 'put on your camera and take a photo'
			if user['username'] == "Admin":
				return redirect(url_for('dashboard'))
			else:
				return redirect(url_for('captcha'))
                         
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)



# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'username' not in session and 'username' !=  "Admin": # if user is not loggedin and not admin redirect to login page
        return redirect(url_for('login')) 
    else:
        msg = f'{session["username"]} , Welcome to the dashboad'

    return render_template('dashboard.html', msg = msg)

	

#FETCH ALL USERS FUNCTION
def everyUser():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users')
    regusers = cursor.fetchall()
    return regusers
  
    
# ALL USERS ROUTE FUNCTION
@app.route('/users', methods =['GET', 'POST'])
def users():
  if 'username' not in session and 'username' != "Admin": # if user is not loggedin and not admin redirect to login page
        return redirect(url_for('login')) 
  else:
      user = everyUser()
      return render_template('users.html', users = user)
 
 
 #FETCH ALL LOGEDIN USERS FUNCTION
def everyLogedin():
     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute('SELECT * FROM users_online')
     allLogedin = cursor.fetchall()
     return allLogedin
 
  
#ALL USERS ONLINE
@app.route('/users-loggedin', methods =['GET', 'POST'])
def users_loggedin():
    if 'username' not in session and 'username' !=  "Admin": # if user is not loggedin and not admin redirect to login page
        return redirect(url_for('login')) 
    else:
       userLoggedIn = everyLogedin()
       return render_template('usersLoggedIn.html', users = userLoggedIn)



# i will get the username and session id when the user is directed to this page
# and re-enter them into the database when a user takes a picture 
@app.route('/capture', methods =['GET', 'POST'])
def captcha():
    
    if 'username' not in session:
         return redirect(url_for('login'))
    
    elif 'username' in session:
        
            # captured = camera

            msg = f'{session["username"]} , make sure your face is in the frame and click on the capture button'
            
                

    return render_template('capture.html', msg = msg)  




##USER HOME PAGE ROOT
@app.route('/home')
def home():
    return render_template('index.html')


###VIDEO FEED FUNCTION
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



##REQUEST FUNCTION
@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST' and request.form.get('click') == 'capture':
        # if request.form.get('click') == 'Capture':
            global capture
            capture=1
            username = session['username']
            captured = capture
            if not captured:
                    redirect(url_for('captcha'))
            else:
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    cursor.execute('INSERT INTO users_online(username, image) VALUES(%s, %s)', (username, captured))
                    mysql.connection.commit()
                    return redirect(url_for('home'))
                
    elif request.method == 'GET':
        return render_template('capture.html')
    return render_template('capture.html')





# LOGOUT FUNCTION
@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))


# DELETE USER FUNCTION
@app.route('/delete/<id_data>', methods = ['GET'])
def delete(id_data):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM users WHERE id = {0}'.format(id_data))
    mysql.connection.commit()
    return redirect(url_for('users'))


# DELETE USER ONLINE FUNCTION
@app.route('/delete-online/<id_data>', methods = ['GET'])
def delete_online(id_data):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM users_online WHERE id = {0}'.format(id_data))
    mysql.connection.commit()
    return redirect(url_for('users_loggedin'))


# REGISTER FUNCTION
@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
		user = cursor.fetchone()
		if user:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, email, password, ))
			mysql.connection.commit()
			msg = 'You have successfully registered. Login now !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)









