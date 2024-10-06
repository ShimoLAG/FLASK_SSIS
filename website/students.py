from flask import Blueprint, render_template, redirect, url_for, request, flash
import MySQLdb.cursors
from . import mysql


students = Blueprint('students', __name__)

#The whole website

@students.route('/', methods=['GET', 'POST'])
def studentsPage():
    def Get_Students():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT ID, FIRST_NAME, LAST_NAME, COURSE_CODE, YEAR, GENDER FROM students')
        student = cursor.fetchall()
        cursor.close()
        return student
    
    def getCourses():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COURSE_CODE, COURSE_NAME FROM courses')
        cour = cursor.fetchall()
        cursor.close()
        return cour
    
    if request.method == 'POST':
        ID = request.form['ID']
        FIRST_NAME = request.form['FIRST_NAME']
        LAST_NAME = request.form['LAST_NAME']
        COURSE_CODE = request.form['COURSE_CODE']
        YEAR = request.form['YEAR']
        GENDER = request.form['GENDER']

        cursor = mysql.connection.cursor()
        
        # Check if the ID already exists
        cursor.execute("SELECT COUNT(*) FROM students WHERE ID = %s", (ID,))
        count = cursor.fetchone()[0]

        if count > 0:
            flash("Error: ID already exists. Please use a different ID.", category="error")
        elif not FIRST_NAME or not LAST_NAME:
            flash("Error: First Name and Last Name cannot be empty.", category="error")
        else:
            # Insert new student if validation passes
            cursor.execute("INSERT INTO students (ID, FIRST_NAME, LAST_NAME, COURSE_CODE, YEAR, GENDER) VALUES (%s, %s, %s, %s, %s, %s)", (ID, FIRST_NAME, LAST_NAME, COURSE_CODE, YEAR, GENDER))
            mysql.connection.commit()
            flash("Student added successfully!", category="success")
        
        cursor.close()
        return redirect(url_for('students.studentsPage'))
    
    studvalue = Get_Students()
    cours = getCourses()

    return render_template('students.html', stud=studvalue, Cval=cours)






#The courses table
@students.route('/courses', methods=['GET', 'POST'])
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
            return redirect(url_for('students.coursesPage'))

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO courses (COURSE_CODE, COURSE_NAME, COLLEGE_CODE) VALUES (%s, %s, %s)", 
                       (COURSE_CODE, COURSE_NAME, COLLEGE_CODE))
        mysql.connection.commit()
        cursor.close()

        flash("Course added successfully", category="success")
        return redirect(url_for('students.coursesPage'))
    
    courvalue = Get_Courses()
    colvalue = GetColleges()

    return render_template('courses.html', courses=courvalue, colleges=colvalue)







#The college table
@students.route('/colleges', methods=['GET', 'POST'])
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
            return redirect(url_for('students.collegesPage'))

        # If the college code does not exist, proceed to insert
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO colleges (COLLEGE_CODE, COLLEGE_NAME) VALUES (%s, %s)", (COLLEGE_CODE, COLLEGE_NAME))
        mysql.connection.commit()
        cursor.close()

        flash("College added successfully", category="success")
        return redirect(url_for('students.collegesPage'))
    
    collvalue = Get_Colleges()

    return render_template('colleges.html', colleges=collvalue)





#Update Routes
@students.route('/collegesUpdate', methods=['POST'])
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
            return redirect(url_for('students.collegesPage'))

        # Update the college code and name if the new college code does not exist
        cur.execute(''' 
                    UPDATE colleges
                    SET COLLEGE_CODE = %s, COLLEGE_NAME = %s
                    WHERE COLLEGE_CODE = %s
                    ''', (NEW_COLLEGE_CODE, COLLEGE_NAME, OLD_COLLEGE_CODE))

        mysql.connection.commit()
        cur.close()

        flash("College updated successfully", category="success")
        return redirect(url_for('students.collegesPage'))

    
@students.route('/coursesUpdate', methods=['POST'])
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
            return redirect(url_for('students.coursesPage'))

        # Update the course code, name, and associated college if the new course code does not exist
        cur.execute(''' 
                    UPDATE courses
                    SET COURSE_CODE = %s, COURSE_NAME = %s, COLLEGE_CODE = %s
                    WHERE COURSE_CODE = %s
                    ''', (NEW_COURSE_CODE, COURSE_NAME, COLLEGE_CODE, OLD_COURSE_CODE))

        mysql.connection.commit()
        cur.close()

        flash("Course updated successfully", category="success")
        return redirect(url_for('students.coursesPage'))

    
@students.route('/studentsUpdate', methods=['POST'])
def studentsUpdate():
    if request.method == 'POST':
        OLD_ID = request.form['OLD_ID']  # Hidden input to hold the original student ID
        NEW_ID = request.form['ID']  # Assuming the ID field is also in the form
        FIRST_NAME = request.form['FIRST_NAME']
        LAST_NAME = request.form['LAST_NAME']
        COURSE_CODE = request.form['COURSE_CODE']
        YEAR = request.form['YEAR']
        GENDER = request.form['GENDER']

        cur = mysql.connection.cursor()

        # Check for empty first name and last name
        if not FIRST_NAME or not LAST_NAME:
            flash("Error: First Name and Last Name cannot be empty.", category="error")
            return redirect(url_for('students.studentsPage'))

        # Check if the new ID already exists
        cur.execute("SELECT COUNT(*) FROM students WHERE ID = %s AND ID != %s", (NEW_ID, OLD_ID))
        count = cur.fetchone()[0]

        if count > 0:
            flash("Error: ID already exists. Please use a different ID.", category="error")
            return redirect(url_for('students.studentsPage'))

        # Update the student information
        cur.execute(''' 
                    UPDATE students 
                    SET ID = %s, FIRST_NAME = %s, LAST_NAME = %s, COURSE_CODE = %s, YEAR = %s, GENDER = %s 
                    WHERE ID = %s 
                    ''', (NEW_ID, FIRST_NAME, LAST_NAME, COURSE_CODE, YEAR, GENDER, OLD_ID))

        mysql.connection.commit()
        cur.close()

        flash("Student updated successfully", category="success")
        return redirect(url_for('students.studentsPage'))


#Delete Routes
@students.route('/deleteStudent/<student_id>', methods=['POST'])
def deleteStudent(student_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE ID = %s", (student_id,))
    mysql.connection.commit()
    cur.close()
    flash("Student deleted successfully", category="success")
    return redirect(url_for('students.studentsPage'))

@students.route('/deleteCourse/<course_code>', methods=['POST'])
def deleteCourse(course_code):
    cur = mysql.connection.cursor()
    
    # Delete the course from the courses table
    cur.execute("DELETE FROM courses WHERE COURSE_CODE = %s", (course_code,))
    mysql.connection.commit()
    cur.close()
    
    flash("Course deleted successfully", category="success")
    return redirect(url_for('students.coursesPage'))

@students.route('/deleteCollege/<college_code>', methods=['POST'])
def deleteCollege(college_code):
    cur = mysql.connection.cursor()
    
    # Delete the college from the colleges table
    cur.execute("DELETE FROM colleges WHERE COLLEGE_CODE = %s", (college_code,))
    mysql.connection.commit()
    cur.close()
    
    flash("College deleted successfully", category="success")
    return redirect(url_for('students.collegesPage'))




#search

@students.route('/search_students', methods=['GET', 'POST'])
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

@students.route('/search_courses', methods=['POST'])
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

@students.route('/search_colleges', methods=['POST'])
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









