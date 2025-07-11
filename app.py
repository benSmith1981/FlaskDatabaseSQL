from flask import Flask, request, render_template_string, render_template
import mysql.connector
import os
from dotenv import load_dotenv

import sqlite3
app = Flask(__name__)
print("DB_HOST:", os.getenv("DB_HOST"))  # for debugging

def get_connection():
    # conn = sqlite3.connect(':memory:')
    # conn = sqlite3.connect('mydatabase.db')
    # Connect to the server without a database
    print("conectin")
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        # database=os.getenv("DB_NAME")
    )

    
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS flasksql")
    conn.database = os.getenv("DB_NAME")

    # Create tables for student and grades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Grades (
            id INTEGER PRIMARY KEY,
            student_id INTEGER,
            subject TEXT,
            grade TEXT,
            FOREIGN KEY (student_id) REFERENCES Students(id)
        )
    ''')
    # Insert data
    students = [
        (1, 'Alice', 18),
        (2, 'Bob', 17),
        (3, 'Charlie', 18),
        (4, 'Denise', 19)
    ]
    grades = [
        (1, 1, 'Maths', 'B'),
        (2, 1, 'English', 'A'),
        (3, 2, 'Maths', 'C'),
        (4, 3, 'English', 'B'),
        (5, 4, 'Maths', 'A'),
        (6, 4, 'English', 'A')
    ]

    cursor.executemany('INSERT INTO Students VALUES (%s, %s, %s)', students)
    cursor.executemany('INSERT INTO Grades VALUES (%s, %s, %s, %s)', grades)

    conn.commit()
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    query = ""
    results = None
    error = None
    columns = []
    message = None  # For success messages
    print("index")
    # Always get table data for display
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()
    student_columns = [description[0] for description in cursor.description]
    cursor.execute("SELECT * FROM Grades")
    grades = cursor.fetchall()
    grade_columns = [description[0] for description in cursor.description]
    conn.close()

    if request.method == 'POST':
        query = request.form['query']
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Split statements by semicolon
            statements = [s.strip() for s in query.strip().split(';') if s.strip()]
            last_stmt = statements[-1].lower() if statements else ""
            # Use executescript to run all statements
            cursor.execute(query)
            conn.commit()
            # If the last statement is SELECT, fetch results
            if last_stmt.startswith("select"):
                # Re-execute the last SELECT only (needed to get results)
                cursor.execute(statements[-1])
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                message = "All statements executed. SELECT results below."
            elif last_stmt.startswith("delete"):
                cursor.execute(query)
                conn.commit()
                message = f"Delete successful. {cursor.rowcount} row(s) deleted."
            elif last_stmt.startswith("insert"):
                cursor.execute(query)
                conn.commit()
                message = f"Insert successful. {cursor.rowcount} row(s) inserted."
            elif last_stmt.startswith("drop"):
                cursor.execute(query)
                conn.commit()
                message = f"Drop successful."
            else:
                error = "Only SELECT, INSERT, DELETE, and DROP statements are supported."
       
        except Exception as e:
            error = str(e)
        conn.close()
    return render_template(
        'index.html',
        query=query,
        results=results,
        error=error,
        columns=columns,
        message=message,
        students=students,
        student_columns=student_columns,
        grades=grades,
        grade_columns=grade_columns
    )
@app.route('/about')
def about():
    return render_template("about.html", active_page="about")


if __name__ == '__main__':
    print("__main__")
    app.run(host="0.0.0.0", port=5000, debug=True)
