from flask import Blueprint, render_template, redirect, url_for, request, flash

import MySQLdb.cursors
import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
load_dotenv()
from . import mysql
from .routes import routes

import re
from flask import flash, redirect, url_for, render_template, request
import MySQLdb

controller = Blueprint('controller', __name__)
#search

@controller.route('/search_students', methods=['GET', 'POST'])
def search_students():
    def get_all_students():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM students')
        students = cursor.fetchall()
        cursor.close()
        return students
    
    if request.method == 'POST':
        search_field = request.form.get('search_field')
        search_value = request.form.get('search_value')

        # Build the query based on the selected search field
        query = f"SELECT * FROM students WHERE {search_field} LIKE %s"
        params = [f"%{search_value}%"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query, params)
        students = cursor.fetchall()
        cursor.close()
        
        return render_template('students.html', stud=students)

    # If it's a GET request, just get all students
    stud = get_all_students()
    return render_template('students.html', stud=stud)

@controller.route('/search_courses', methods=['POST'])
def search_courses():
    search_field = request.form['search_field']
    search_value = request.form['search_value']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Example query that depends on the selected search field
    query = f"SELECT * FROM courses WHERE {search_field} LIKE %s"
    cursor.execute(query, (f"%{search_value}%",))
    
    results = cursor.fetchall()
    cursor.close()

    return render_template('courses.html', courses=results)

@controller.route('/search_colleges', methods=['POST'])
def search_colleges():
    search_field = request.form['search_field']
    search_value = request.form['search_value']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Example query that depends on the selected search field
    query = f"SELECT * FROM colleges WHERE {search_field} LIKE %s"
    cursor.execute(query, (f"%{search_value}%",))
    
    results = cursor.fetchall()
    cursor.close()

    return render_template('colleges.html', colleges=results)



#Update Routes
@controller.route('/collegesUpdate', methods=['POST'])
def collegesUpdate():
    if request.method == 'POST':
        OLD_COLLEGE_CODE = request.form['OLD_COLLEGE_CODE']  # Hidden input to hold original code
        NEW_COLLEGE_CODE = request.form['NEW_COLLEGE_CODE']
        COLLEGE_NAME = request.form['COLLEGE_NAME']

        cur = mysql.connection.cursor()

        # Check if the new college code already exists (excluding the old college code)
        cur.execute("SELECT COUNT(*) FROM colleges WHERE COLLEGE_CODE = %s AND COLLEGE_CODE != %s", (NEW_COLLEGE_CODE, OLD_COLLEGE_CODE))
        exists = cur.fetchone()[0] > 0
        
        if exists:
            flash("Error: College code already exists!", category="error")
            return redirect(url_for('routes.collegesPage'))

        # Update the college code and name if the new college code does not exist
        cur.execute(''' 
                    UPDATE colleges
                    SET COLLEGE_CODE = %s, COLLEGE_NAME = %s
                    WHERE COLLEGE_CODE = %s
                    ''', (NEW_COLLEGE_CODE, COLLEGE_NAME, OLD_COLLEGE_CODE))

        mysql.connection.commit()
        cur.close()

        flash("College updated successfully", category="success")
        return redirect(url_for('routes.collegesPage'))

    
@controller.route('/coursesUpdate', methods=['POST'])
def coursesUpdate():
    if request.method == 'POST':
        OLD_COURSE_CODE = request.form['OLD_COURSE_CODE']  # Hidden input to hold original course code
        NEW_COURSE_CODE = request.form['NEW_COURSE_CODE']
        COURSE_NAME = request.form['COURSE_NAME']
        COLLEGE_CODE = request.form['COLLEGE_CODE']

        cur = mysql.connection.cursor()

        # Check if the new course code already exists (excluding the old course code)
        cur.execute("SELECT COUNT(*) FROM courses WHERE COURSE_CODE = %s AND COURSE_CODE != %s", (NEW_COURSE_CODE, OLD_COURSE_CODE))
        exists = cur.fetchone()[0] > 0
        
        if exists:
            flash("Error: Course code already exists!", category="error")
            return redirect(url_for('routes.coursesPage'))

        # Update the course code, name, and associated college if the new course code does not exist
        cur.execute(''' 
                    UPDATE courses
                    SET COURSE_CODE = %s, COURSE_NAME = %s, COLLEGE_CODE = %s
                    WHERE COURSE_CODE = %s
                    ''', (NEW_COURSE_CODE, COURSE_NAME, COLLEGE_CODE, OLD_COURSE_CODE))

        mysql.connection.commit()
        cur.close()

        flash("Course updated successfully", category="success")
        return redirect(url_for('routes.coursesPage'))

    
@controller.route('/studentsUpdate', methods=['POST'])
def studentsUpdate():
    if request.method == 'POST':
        OLD_ID = request.form['OLD_ID']  # Hidden input to hold the original student ID
        NEW_ID = request.form['ID']  # Assuming the ID field is also in the form
        IMAGE = request.form['IMAGE']
        FIRST_NAME = request.form['FIRST_NAME']
        LAST_NAME = request.form['LAST_NAME']
        COURSE_CODE = request.form['COURSE_CODE']
        YEAR = request.form['YEAR']
        GENDER = request.form['GENDER']

        cur = mysql.connection.cursor()

        # Check for empty first name and last name
        if not FIRST_NAME or not LAST_NAME:
            flash("Error: First Name and Last Name cannot be empty.", category="error")
            return redirect(url_for('routes.studentsPage'))

        # Check if the new ID already exists
        cur.execute("SELECT COUNT(*) FROM students WHERE ID = %s AND ID != %s", (NEW_ID, OLD_ID))
        count = cur.fetchone()[0]

        if count > 0:
            flash("Error: ID already exists. Please use a different ID.", category="error")
            return redirect(url_for('routes.studentsPage'))

        # Update the student information
        cur.execute(''' 
                    UPDATE students 
                    SET ID = %s, IMAGE = %s, FIRST_NAME = %s, LAST_NAME = %s, COURSE_CODE = %s, YEAR = %s, GENDER = %s 
                    WHERE ID = %s 
                    ''', (NEW_ID, IMAGE, FIRST_NAME, LAST_NAME, COURSE_CODE, YEAR, GENDER, OLD_ID))

        mysql.connection.commit()
        cur.close()

        flash("Student updated successfully", category="success")
        return redirect(url_for('routes.studentsPage'))


#Delete Routes
@controller.route('/deleteStudent/<student_id>', methods=['POST'])
def deleteStudent(student_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE ID = %s", (student_id,))
    mysql.connection.commit()
    cur.close()
    flash("Student deleted successfully", category="success")
    return redirect(url_for('routes.studentsPage'))

@controller.route('/deleteCourse/<course_code>', methods=['POST'])
def deleteCourse(course_code):
    cur = mysql.connection.cursor()
    
    # Delete the course from the courses table
    cur.execute("DELETE FROM courses WHERE COURSE_CODE = %s", (course_code,))
    mysql.connection.commit()
    cur.close()
    
    flash("Course deleted successfully", category="success")
    return redirect(url_for('routes.coursesPage'))

@controller.route('/deleteCollege/<college_code>', methods=['POST'])
def deleteCollege(college_code):
    cur = mysql.connection.cursor()
    
    # Delete the college from the colleges table
    cur.execute("DELETE FROM colleges WHERE COLLEGE_CODE = %s", (college_code,))
    mysql.connection.commit()
    cur.close()
    
    flash("College deleted successfully", category="success")
    return redirect(url_for('routes.collegesPage'))
