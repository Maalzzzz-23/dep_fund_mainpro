from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"
DATABASE = "database.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Students Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                            admission_number TEXT PRIMARY KEY,
                            name TEXT,
                            email_id TEXT UNIQUE,
                            dob TEXT,
                            class TEXT
                          )''')
        
        # Staff Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS staff (
                            staff_id TEXT PRIMARY KEY,
                            name TEXT,
                            email_id TEXT UNIQUE,
                            dob TEXT
                          )''')
        
        db.commit()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    email = request.form['email']
    dob = request.form['dob']
    db = get_db()
    
    student = db.execute("SELECT * FROM students WHERE email_id = ? AND dob = ?", (email, dob)).fetchone()
    staff = db.execute("SELECT * FROM staff WHERE email_id = ? AND dob = ?", (email, dob)).fetchone()
    
    if student:
        session['user'] = student['name']
        session['role'] = 'student'
        return redirect(url_for('student_home'))
    elif staff:
        session['user'] = staff['name']
        session['role'] = 'staff'
        return redirect(url_for('staff_home'))
    else:
        return "Invalid Credentials", 401

@app.route('/student_home')
def student_home():
    if 'user' in session and session['role'] == 'student':
        return render_template('student_home.html', name=session['user'])
    return redirect(url_for('login'))

@app.route('/staff_home')
def staff_home():
    if 'user' in session and session['role'] == 'staff':
        db = get_db()
        classes = db.execute("SELECT DISTINCT class FROM students").fetchall()
        class_list = [row["class"] for row in classes]
        return render_template('staff_home.html', name=session['user'], classes=class_list)
    return redirect(url_for('login'))

@app.route('/get_students_by_class/<class_name>')
def get_students_by_class(class_name):
    db = get_db()
    students = db.execute("SELECT admission_number, name, email_id FROM students WHERE class = ?", (class_name,)).fetchall()
    student_list = [{"admission_number": row["admission_number"], "name": row["name"], "email_id": row["email_id"]} for row in students]
    return jsonify({"students": student_list})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
