# queries.py

# Queries for students
GET_COURSES = "SELECT COURSE_CODE, COURSE_NAME FROM courses"

SEARCH_STUDENTS_NONE = """
    SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
           students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
    FROM students
    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
    WHERE students.COURSE_CODE IS NULL
    LIMIT %s OFFSET %s
"""
COUNT_STUDENTS_NONE = """
    SELECT COUNT(*) AS total
    FROM students
    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
    WHERE students.COURSE_CODE IS NULL
"""

SEARCH_COURSE_CODE = """
    SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
           students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
    FROM students
    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
    WHERE students.COURSE_CODE LIKE %s OR courses.COURSE_NAME LIKE %s
    LIMIT %s OFFSET %s
"""
COUNT_COURSE_CODE = """
    SELECT COUNT(*) AS total
    FROM students
    LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
    WHERE students.COURSE_CODE LIKE %s OR courses.COURSE_NAME LIKE %s
"""

DELETE_STUDENT = "DELETE FROM students WHERE ID = %s"
DELETE_COURSE = "DELETE FROM courses WHERE COURSE_CODE = %s"
DELETE_COLLEGE = "DELETE FROM colleges WHERE COLLEGE_CODE = %s"

UPDATE_COLLEGE = """
    UPDATE colleges
    SET COLLEGE_CODE = %s, COLLEGE_NAME = %s
    WHERE COLLEGE_CODE = %s
"""

UPDATE_COURSE = """
    UPDATE courses
    SET COURSE_CODE = %s, COURSE_NAME = %s, COLLEGE_CODE = %s
    WHERE COURSE_CODE = %s
"""

UPDATE_STUDENT = """
    UPDATE students
    SET ID = %s, IMAGE = %s, FIRST_NAME = %s, LAST_NAME = %s, COURSE_CODE = %s, YEAR = %s, GENDER = %s
    WHERE ID = %s
"""

# Example of a function for dynamic queries
def search_students_by_field(search_field):
    return f"""
        SELECT students.ID, students.IMAGE, students.FIRST_NAME, students.LAST_NAME,
               students.COURSE_CODE, courses.COURSE_NAME, students.YEAR, students.GENDER
        FROM students
        LEFT JOIN courses ON students.COURSE_CODE = courses.COURSE_CODE
        WHERE students.{search_field} LIKE %s
        LIMIT %s OFFSET %s
    """
