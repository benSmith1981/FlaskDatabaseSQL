from flask import Flask, request, render_template_string, render_template

import sqlite3
app = Flask(__name__)

# Function to set up the database and return a connection
def get_connection():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''
        CREATE TABLE Students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE Grades (
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
    cursor.executemany('INSERT INTO Students VALUES (?, ?, ?)', students)
    cursor.executemany('INSERT INTO Grades VALUES (?, ?, ?, ?)', grades)
    conn.commit()
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    query = ""
    results = None
    error = None
    columns = []
    if request.method == 'POST':
        query = request.form['query']
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            # Only show results for SELECT queries
            if query.strip().lower().startswith("select"):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
            else:
                error = "Please enter a SELECT query to see results."
        except Exception as e:
            error = str(e)
        conn.close()
    return render_template('index.html', query=query, results=results, error=error, columns=columns)

if __name__ == '__main__':
    app.run(debug=True)