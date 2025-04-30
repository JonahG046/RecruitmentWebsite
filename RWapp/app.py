from flask import Flask, redirect, url_for, render_template, request, flash, redirect, session, jsonify
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import MySQLdb
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = "Aidan"
bcrypt = Bcrypt(app)

app.config['MYSQL_HOST'] = 'rw-database.c5s0mywewz4g.us-east-2.rds.amazonaws.com' 
app.config['MYSQL_USER'] = 'JGadmin'
app.config['MYSQL_PASSWORD'] = 'ILoveMae1234'
app.config['MYSQL_DB'] = 'u612285796_firstcohort'

mydb = MySQL(app)
#All app.route() statements direct you to the given pages of the web application

@app.route('/')
def home():
  return render_template('HomeRW.html',page='Home', foot = True)

@app.route('/Our_Program')
def ourProgram():
  return render_template('OurProgram.html',page='About', foot = True)

@app.route('/Minnpoly')
def minnpoly():
  return render_template('Minnpoly.html',page='About', foot = True)

@app.route('/Industry_Partners')
def indPart():
  return render_template('Indpart.html',page='About', foot = True)

@app.route('/Prerequisites/MSU')
def prereqMSU():
  return render_template('prereqMSU.html',page='Preq', foot = True)

@app.route('/Prerequisites/Courses')
def prereqCourses():
  return render_template('prereq.html',page='Preq', foot = True)

@app.route('/Apply')
def apply():
  return render_template('Application.html',page='Apply', foot = True)

@app.route('/Frequently_Asked_Questions')
def faq():
  return render_template('FAQRW.html',page='FAQ', foot = True)

@app.route('/Calendar')
def calendar():
  return render_template('Calendar.html', foot = False)

@app.route('/Profile')
def profile():
    return render_template('profile.html', page='Profile', foot = False)

@app.route('/Settings', methods = ['GET','POST'])
def accntSettings():
  if request.method == 'POST':
    pass
  return render_template("Settings.html", foot = False)

@app.route('/Login', methods = ['GET', 'POST'])
def login():
  foot = False
  #cursor for the mySQL database
  cursor = mydb.connection.cursor(MySQLdb.cursors.DictCursor)
  if request.method == 'POST':
    #stores the form data into logForm dict
    logForm = request.form
    #cursor select the account used for the email
    cursor.execute("SELECT * FROM profiles WHERE email = %s", (logForm['email'],))
    #checks if there is an account with the specific email address
    accnt = cursor.fetchone()
    if accnt is not None:
      print('gets here when email is right')
      #checks the password written in the form with the encrypted password
      vp = bcrypt.check_password_hash(accnt['password'], logForm['password'])
      #statement executes if there is an account under the given email 
      #and that accounts password matches with the encrypted password
      if vp:
        #if everything is right it sets up the session for the account
        flash("Success: You're signed in!")
        session['user'] = accnt['email']
        session['first'] = accnt['first_name']
        session['last'] = accnt['last_name']
        session['phone'] = accnt['phone']
        session['starId'] = accnt['starid']
        cursor.close()
        return redirect(url_for('home'))
      else:
        cursor.close()
        flash("Error: Username or password is incorrect")
        return redirect(url_for('login'))
    else:
      cursor.close()
      flash("Error: Username or password is incorrect")
      return redirect(url_for('login'))
  #renders the login page
  cursor.close()
  return render_template('LoginRW.html', foot = False)

@app.route('/SignUp', methods=['GET','POST'])
def signUp():
  foot = False
  #cursor for database used to search for duplicate entires
  cursor = mydb.connection.cursor(MySQLdb.cursors.DictCursor)
  #mydb.cursor()
  if request.method == 'POST':
    myform = request.form
    #gets the data from the signUp form
    firstName = myform['first']
    lastName = myform['last']
    email = myform['email']
    password = myform['password']
    #generates hashcode for the password entered
    hashPass = bcrypt.generate_password_hash(password).decode("utf-8")
    starId = myform['starid']
    phone = myform['phone']
    #cursor finds duplicate entries (if there are any)
    cursor.execute("SELECT email FROM profiles WHERE email = %s", (email,))
    dup = cursor.fetchone()
    #checks for duplicate email entries
    if dup:
      cursor.close()
      flash("You already have an account Please login.")
      return redirect(url_for('login'))
    else:
      #inserts the new entry into the profiles table in MySql
      cursor.execute("INSERT INTO profiles (first_name, last_name, phone, email, starid, password) VALUES (%s,%s,%s,%s,%s,%s)", ( firstName, lastName, phone, email, starId, hashPass))
      mydb.connection.commit()
      #logs the user in, session uses email to identify who is signed in
      session['user'] = email
      session['first'] = firstName
      session['last'] = lastName
      session['phone'] = phone
      session['starId'] = starId
      cursor.close()
      #I want to look into changing the color of the flash box for this statement
      flash("Success: You're all signed up!")
      return redirect(url_for('home'))
  cursor.close()
  return render_template("SignUpRW.html", foot = False)

@app.route('/Logout')
def logout():
  #this removes the users account information from the session
  #signing them out
  session.pop('user', None)
  session.pop('first', None)
  session.pop('last', None)
  session.pop('phone', None)
  session.pop('starId', None)
  return redirect(url_for('home'))


@app.route('/api/program_info', methods=['GET'])
def api_program_info():
  program_info = {
      "program_name": "Minnpolly Software Engineering Program",
      "description": "A comprehensive program combining academic learning with real-world industry experience.",
      "requirements": ["Strong programming skills", "Motivated to work in a team environment"],
      "duration": "2 and a half years",
      "credits": 60
  }
  return jsonify(program_info)

@app.route('/api/faq', methods=['GET'])
def api_faq():
  faqs = [
      {
          "question": "What is the duration of the program?",
          "answer": "The program lasts for 2 and a half years."
      },
      {
          "question": "What are the prerequisites for the program?",
          "answer": "You need to have strong programming skills and be motivated to work in a team environment."
      }
  ]
  return jsonify(faqs)

@app.route('/api/interviews/slots', methods=['GET'])
def api_interview_slots():
  # Example data for interview slots
  interview_slots = [
      {
          "date": "2023-10-01",
          "time": "10:00 AM",
          "location": "Minnesota State University, Mankato"
      },
      {
          "date": "2023-10-01",
          "time": "11:00 AM",
          "location": "online"
      },
      {
          "date": "2023-10-02",
          "time": "09:00 AM",
          "location": "Minnesota State University, Mankato"
      }
  ]
  return jsonify(interview_slots)

@app.route('/api/login', methods=['POST'])
def api_login():
  data = request.get_json()
  email = data.get('email')
  password = data.get('password')

  if not email or not password:
    return jsonify({"error": "Email and password are required."}), 400
  
  cursor = mydb.connection.cursor(MySQLdb.cursors.DictCursor)
  cursor.execute("SELECT * FROM profiles WHERE email = %s", (email,))
  user = cursor.fetchone()

  if user:
    if bcrypt.check_password_hash(user['password'], password):
      session['user'] = user['email']
      session['first'] = user['first_name']
      session['last'] = user['last_name']
      session['phone'] = user['phone']
      session['starId'] = user['starid']
      cursor.close()
      return jsonify({
          "message": "Login successful",
          "first_name": user['first_name'],
          "last_name": user['last_name'],
          "email": user['email']
        }), 200
    else:
      cursor.close()
      return jsonify({"error": "Invalid password."}), 401
  else:
    cursor.close()
    return jsonify({"error": "User not found."}), 404







if __name__ == '__main__':
  app.run(debug=True)
  #To show the footer in the template
  foot = True
