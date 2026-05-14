import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cohort TEXT NOT NULL,
        age INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        credits INTEGER NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        course_id INTEGER,
        score INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
    )
    """)
    
    # Seed data
    cursor.executemany("""
    INSERT INTO students (name, cohort, age) VALUES (?, ?, ?)
    """, [
        ('Alice', 'A1', 20),
        ('Bob', 'A1', 22),
        ('Charlie', 'B2', 21),
        ('Diana', 'B2', 23),
        ('Eve', 'A1', 19)
    ])
    
    cursor.executemany("""
    INSERT INTO courses (title, credits) VALUES (?, ?)
    """, [
        ('Math 101', 3),
        ('Physics 201', 4),
        ('History 101', 3)
    ])
    
    cursor.executemany("""
    INSERT INTO enrollments (student_id, course_id, score) VALUES (?, ?, ?)
    """, [
        (1, 1, 95),
        (1, 2, 88),
        (2, 1, 75),
        (3, 3, 90),
        (4, 2, 85),
        (5, 1, 92)
    ])
    
    conn.commit()
    conn.close()
    print("Database initialized with seed data.")

if __name__ == "__main__":
    init_db()
