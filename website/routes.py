from flask import Blueprint, render_template, redirect, url_for, request, flash
import MySQLdb.cursors
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
load_dotenv()
from . import mysql

# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=fssis
# DB_USERNAME=root
# DB_PASSWORD=root
# SECRET_KEY=thisisarandomsecretkey1111
# BOOTSTRAP_SERVE_LOCAL=True
# PIPENV_VENV_IN_PROJECT=1
# CLOUDINARY_URL=cloudinary://419821381875283:Ca2sfgxZK8i4e24vqHPi0ED62Yk@dgmaqsdil

routes = Blueprint('routes', __name__)

#The whole website

import re
from flask import flash, redirect, url_for, render_template, request
import MySQLdb

#student table

@routes.route('/', methods=['GET', 'POST'])
def studentsPage():
    def Get_Students(offset, limit):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
        SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
               students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
        FROM students
        LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
        LIMIT %s OFFSET %s
        """, (limit, offset))
        student = cursor.fetchall()
        cursor.close()
        return student

    def getCourses():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COURSE_CODE, COURSE_NAME FROM courses')
        cour = cursor.fetchall()
        cursor.close()
        return cour

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # Get total student count for pagination
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT COUNT(*) AS total FROM students')
    total_students = cursor.fetchone()['total']
    cursor.close()

    # Calculate total pages
    total_pages = (total_students + per_page - 1) // per_page

    # Ensure page is within range
    if page < 1:
        flash("Invalid page number.", "error")
        return redirect(url_for('routes.studentsPage', page=1))
    if page > total_pages:
        flash("Page out of range.", "error")
        return redirect(url_for('routes.studentsPage', page=total_pages))

    if request.method == 'POST':
        ID = request.form['ID']
        IMAGE = request.form.get('IMAGE', '').strip()  # Get IMAGE, default to an empty string
        FIRST_NAME = request.form['FIRST_NAME']
        LAST_NAME = request.form['LAST_NAME']
        COURSE_CODE = request.form['COURSE_CODE']
        YEAR = request.form['YEAR']
        GENDER = request.form['GENDER']

        # Set default image if IMAGE is empty
        if not IMAGE:
            IMAGE = '/static/images/default-profile.jpg'  # Ensure this path points to your default image

        cursor = mysql.connection.cursor()

        # Check if the ID already exists
        cursor.execute("SELECT COUNT(*) FROM students WHERE ID = %s", (ID,))
        count = cursor.fetchone()[0]

        # Regular expression for validating ID format (0000-0000)
        id_pattern = r'^\d{4}-\d{4}$'

        if count > 0:
            flash("Error: ID already exists. Please use a different ID.", category="error")
        elif not FIRST_NAME or not LAST_NAME:
            flash("Error: First Name and Last Name cannot be empty.", category="error")
        elif not re.match(id_pattern, ID):
            flash("Error: ID must follow the format 0000-0000.", category="error")
        else:
            # Insert new student if validation passes
            cursor.execute(
                "INSERT INTO students (ID, IMAGE, FIRST_NAME, LAST_NAME, COURSE_CODE, YEAR, GENDER) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (ID, IMAGE, FIRST_NAME, LAST_NAME, COURSE_CODE, YEAR, GENDER)
            )
            mysql.connection.commit()
            flash("Student added successfully!", category="success")

        cursor.close()
        return redirect(url_for('routes.studentsPage'))

    # Fetch paginated students and courses
    studvalue = Get_Students(offset, per_page)
    cours = getCourses()

    return render_template(
        'students.html',
        stud=studvalue,
        Cval=cours,
        current_page=page,
        total_pages=total_pages
    )


#The courses table
@routes.route('/courses', methods=['GET', 'POST'])
def coursesPage():
    def Get_Courses():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COURSE_CODE, COURSE_NAME, COLLEGE_CODE FROM courses')
        courses = cursor.fetchall()
        cursor.close()
        return courses
    
    def GetColleges():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COLLEGE_CODE, COLLEGE_NAME FROM colleges')
        colleges = cursor.fetchall()
        cursor.close()
        return colleges

    if request.method == 'POST':
        COURSE_CODE = request.form['COURSE_CODE']
        COURSE_NAME = request.form['COURSE_NAME']
        COLLEGE_CODE = request.form['COLLEGE_CODE']

        # Create a cursor to check if the course code already exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM courses WHERE COURSE_CODE = %s", (COURSE_CODE,))
        exists = cursor.fetchone()[0] > 0
        cursor.close()

        if exists:
            flash("Error: Course code already exists!", category="error")
            return redirect(url_for('routes.coursesPage'))

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO courses (COURSE_CODE, COURSE_NAME, COLLEGE_CODE) VALUES (%s, %s, %s)", 
                       (COURSE_CODE, COURSE_NAME, COLLEGE_CODE))
        mysql.connection.commit()
        cursor.close()

        flash("Course added successfully", category="success")
        return redirect(url_for('routes.coursesPage'))
    
    courvalue = Get_Courses()
    colvalue = GetColleges()

    return render_template('courses.html', courses=courvalue, colleges=colvalue)







#The college table
@routes.route('/colleges', methods=['GET', 'POST'])
def collegesPage():
    def Get_Colleges():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COLLEGE_CODE, COLLEGE_NAME FROM colleges')
        college = cursor.fetchall()
        cursor.close()
        return college
    
    if request.method == 'POST':
        COLLEGE_CODE = request.form['COLLEGE_CODE']
        COLLEGE_NAME = request.form['COLLEGE_NAME']
        
        # Create a cursor to check if the college code already exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM colleges WHERE COLLEGE_CODE = %s", (COLLEGE_CODE,))
        exists = cursor.fetchone()[0] > 0
        cursor.close()

        if exists:
            flash("Error: College code already exists!", category="error")
            return redirect(url_for('routes.collegesPage'))

        # If the college code does not exist, proceed to insert
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO colleges (COLLEGE_CODE, COLLEGE_NAME) VALUES (%s, %s)", (COLLEGE_CODE, COLLEGE_NAME))
        mysql.connection.commit()
        cursor.close()

        flash("College added successfully", category="success")
        return redirect(url_for('routes.collegesPage'))
    
    collvalue = Get_Colleges()

    return render_template('colleges.html', colleges=collvalue)












