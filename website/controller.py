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
    try:
        # Fetch the list of courses
        def getCourses():
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT COURSE_CODE, COURSE_NAME FROM courses')
            cours = cursor.fetchall()
            cursor.close()
            return cours

        if request.method == 'POST' or 'search_field' in request.args:
            search_field = request.args.get('search_field', request.form.get('search_field'))
            search_value = request.args.get('search_value', request.form.get('search_value'))

            # Validate search_field
            valid_fields = {'ID', 'FIRST_NAME', 'LAST_NAME', 'COURSE_CODE', 'COURSE_NAME', 'YEAR', 'GENDER'}
            if search_field not in valid_fields:
                flash("Invalid search field", "error")
                return redirect(url_for('routes.studentsPage'))

            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = 10
            offset = (page - 1) * per_page

            # Handle special case for searching 'none' to find null course codes
            if search_field in ['COURSE_CODE', 'COURSE_NAME'] and search_value.strip().lower() == 'none':
                query = """
                    SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
                           students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.COURSE_CODE IS NULL
                    LIMIT %s OFFSET %s
                """
                params = [per_page, offset]
                count_query = """
                    SELECT COUNT(*) AS total
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.COURSE_CODE IS NULL
                """
                count_params = []
            elif search_field == 'COURSE_CODE':
                query = """
                    SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
                           students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.COURSE_CODE LIKE %s OR courses.COURSE_NAME LIKE %s
                    LIMIT %s OFFSET %s
                """
                params = [f"%{search_value}%", f"%{search_value}%", per_page, offset]
                count_query = """
                    SELECT COUNT(*) AS total
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.COURSE_CODE LIKE %s OR courses.COURSE_NAME LIKE %s
                """
                count_params = [f"%{search_value}%", f"%{search_value}%"]
            elif search_field == 'COURSE_NAME':
                query = """
                    SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
                           students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE courses.COURSE_NAME LIKE %s
                    LIMIT %s OFFSET %s
                """
                params = [f"%{search_value}%", per_page, offset]
                count_query = """
                    SELECT COUNT(*) AS total
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE courses.COURSE_NAME LIKE %s
                """
                count_params = [f"%{search_value}%"]
            elif search_field == 'GENDER':
                query = """
                    SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
                           students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.GENDER = %s
                    LIMIT %s OFFSET %s
                """
                params = [search_value, per_page, offset]
                count_query = """
                    SELECT COUNT(*) AS total
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.GENDER = %s
                """
                count_params = [search_value]
            else:
                query = """
                    SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
                           students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.{search_field} LIKE %s
                    LIMIT %s OFFSET %s
                """
                query = query.format(search_field=search_field)
                params = [f"%{search_value}%", per_page, offset]
                count_query = """
                    SELECT COUNT(*) AS total
                    FROM students
                    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
                    WHERE students.{search_field} LIKE %s
                """
                count_query = count_query.format(search_field=search_field)
                count_params = [f"%{search_value}%"]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, params)
            students = cursor.fetchall()

            cursor.execute(count_query, count_params)
            total_students = cursor.fetchone()['total']
            cursor.close()

            total_pages = (total_students + per_page - 1) // per_page
            courses = getCourses()

            return render_template(
                'students.html',
                stud=students,
                Cval=courses,
                current_page=page,
                total_pages=total_pages,
                search_field=search_field,
                search_value=search_value
            )

        # If GET request, redirect to the main student page
        return redirect(url_for('routes.studentsPage'))
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(traceback.format_exc())
        flash("An error occurred while processing your request.", "error")
        return redirect(url_for('routes.studentsPage'))



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
        NEW_ID = request.form['ID']
        IMAGE = request.form.get('IMAGE', '').strip()
        FIRST_NAME = request.form['FIRST_NAME']
        LAST_NAME = request.form['LAST_NAME']
        COURSE_CODE = request.form['COURSE_CODE']
        YEAR = request.form['YEAR']
        GENDER = request.form['GENDER']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the current image for the student if IMAGE is empty
        if not IMAGE:
            cur.execute("SELECT IMAGE FROM students WHERE ID = %s", (OLD_ID,))
            current_image = cur.fetchone()
            if current_image:  # Check if a result exists
                IMAGE = current_image['IMAGE'] if current_image['IMAGE'] else '/static/images/default-profile.jpg'
            else:
                IMAGE = '/static/images/default-profile.jpg'  # Default if no existing image

        # Check for empty first name and last name
        if not FIRST_NAME or not LAST_NAME:
            flash("Error: First Name and Last Name cannot be empty.", category="error")
            return redirect(url_for('routes.studentsPage'))

        # Check if the new ID already exists (excluding the current record)
        cur.execute("SELECT COUNT(*) AS count FROM students WHERE ID = %s AND ID != %s", (NEW_ID, OLD_ID))
        result = cur.fetchone()
        count = result['count'] if result else 0  # Safely handle None

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
