from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Required for flash messages (and sessions)

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            grade TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- Seed Data (Only Once) ---
def seed_data():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    count = c.fetchone()[0]
    if count == 0:
        students = [
            ("Alice", 14, "8th"),
            ("Bob", 15, "9th"),
            ("Charlie", 13, "7th")
        ]
        c.executemany("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", students)
    conn.commit()
    conn.close()

# --- Remove Duplicate Records ---
def remove_duplicates():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''
        DELETE FROM students
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM students
            GROUP BY name, age, grade
        )
    ''')
    conn.commit()
    conn.close()

# --- Routes ---

@app.route('/')
def index():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    students = c.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))
        conn.commit()
        conn.close()

        flash("Student added successfully!", "success")
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()

    flash("Student deleted.", "warning")
    return redirect(url_for('index'))

# --- Run Server ---
if __name__ == '__main__':
    init_db()
    remove_duplicates()  # Clean any existing repeated entries
    seed_data()          # Insert dummy data if DB is empty
    app.run(debug=True)
