import sqlite3

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute('''
    CREATE TABLE IF NOT EXISTS interviewers (
        email TEXT PRIMARY KEY,
        token TEXT,
        availability_filled INTEGER DEFAULT 0
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS availabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interviewer_email TEXT,
        day TEXT,
        start_time TEXT,
        end_time TEXT,
        FOREIGN KEY(interviewer_email) REFERENCES interviewers(email)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        email TEXT PRIMARY KEY,
        booked_slot_id INTEGER,
        FOREIGN KEY(booked_slot_id) REFERENCES availabilities(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_email TEXT,
        interviewer_email TEXT,
        day TEXT,
        start_time TEXT,
        end_time TEXT
    )''')
    conn.commit()

def add_interviewer(email, token):
    c.execute("INSERT INTO interviewers (email, token) VALUES (?, ?)", (email, token))
    conn.commit()

def get_interviewer_by_token(token):
    c.execute("SELECT email FROM interviewers WHERE token=?", (token,))
    return c.fetchone()

def mark_availability_filled(email):
    c.execute("UPDATE interviewers SET availability_filled=1 WHERE email=?", (email,))
    conn.commit()

def save_availability(email, availabilities):
    for day, start_time, end_time in availabilities:
        c.execute('''
            INSERT INTO availabilities (interviewer_email, day, start_time, end_time)
            VALUES (?, ?, ?, ?)
        ''', (email, day, start_time, end_time))
    conn.commit()

def get_available_slots():
    c.execute('''
    SELECT id, interviewer_email, day, start_time, end_time
    FROM availabilities
    WHERE id NOT IN (SELECT booked_slot_id FROM candidates)
    ''')
    return c.fetchall()

def book_slot(candidate_email, slot_id):
    c.execute('INSERT INTO candidates (email, booked_slot_id) VALUES (?, ?)', (candidate_email, slot_id))
    c.execute('SELECT interviewer_email, day, start_time, end_time FROM availabilities WHERE id=?', (slot_id,))
    slot = c.fetchone()
    c.execute('''
        INSERT INTO bookings (candidate_email, interviewer_email, day, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (candidate_email, slot[0], slot[1], slot[2], slot[3]))
    conn.commit()

def get_booking_details(candidate_email):
    c.execute('SELECT interviewer_email, day, start_time, end_time FROM bookings WHERE candidate_email=?', (candidate_email,))
    return c.fetchone()
