import streamlit as st
import sqlite3
import smtplib
import uuid
from email.message import EmailMessage

# =============== DATABASE SETUP =================
conn = sqlite3.connect('calendar_booking.db', check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS interviewers (
        email TEXT PRIMARY KEY,
        token TEXT,
        availability_filled INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS availabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interviewer_email TEXT,
        day TEXT,
        start_time TEXT,
        end_time TEXT,
        FOREIGN KEY(interviewer_email) REFERENCES interviewers(email)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        email TEXT PRIMARY KEY,
        booked_slot_id INTEGER,
        FOREIGN KEY(booked_slot_id) REFERENCES availabilities(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_email TEXT,
        interviewer_email TEXT,
        day TEXT,
        start_time TEXT,
        end_time TEXT
    )''')
    conn.commit()

create_tables()

# =============== EMAIL SENDER =================
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your_email@gmail.com'
SENDER_PASSWORD = 'your_email_password'

def send_email(to_email, subject, body):
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# =============== STREAMLIT APP =================

st.title("📅 Interview Scheduling System")

menu = st.sidebar.selectbox("Select Role", ["HR - Add Interviewers", "Interviewer - Fill Availability"])

if menu == "HR - Add Interviewers":
    st.header("🔹 Add Interviewer Emails")
    with st.form(key='add_interviewer_form'):
        interviewer_email = st.text_input("Enter Interviewer's Email:")
        submit_btn = st.form_submit_button("Submit")

        if submit_btn:
            token = str(uuid.uuid4())
            try:
                c.execute("INSERT INTO interviewers (email, token) VALUES (?,?)", (interviewer_email, token))
                conn.commit()

                link = f"http://localhost:8501/?page=interviewer_availability&token={token}"
                body = f"Hi,\n\nPlease set your availability for interviews using the link below:\n{link}\n\nThank you!"
                send_email(interviewer_email, "Set your availability", body)

                st.success(f"Interviewer {interviewer_email} added and email sent!")
            except sqlite3.IntegrityError:
                st.error("Interviewer already exists.")

elif menu == "Interviewer - Fill Availability":
    st.header("🔹 Fill Your Availability")

    query_params = st.experimental_get_query_params()
    token = query_params.get('token', [None])[0]

    if token:
        c.execute("SELECT email FROM interviewers WHERE token=?", (token,))
        row = c.fetchone()
        if row:
            interviewer_email = row[0]
            st.subheader(f"Welcome {interviewer_email} 👋")

            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            with st.form(key='availability_form'):
                slots = []
                for day in days:
                    st.markdown(f"**{day}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        start_time = st.time_input(f"{day} Start", key=f"{day}_start")
                    with col2:
                        end_time = st.time_input(f"{day} End", key=f"{day}_end")

                    slots.append((day, start_time.strftime("%H:%M"), end_time.strftime("%H:%M")))

                submit_avail_btn = st.form_submit_button("Submit Availability")

                if submit_avail_btn:
                    for slot in slots:
                        day, start, end = slot
                        if start != end:  # Only if user set times
                            c.execute("INSERT INTO availabilities (interviewer_email, day, start_time, end_time) VALUES (?,?,?,?)",
                                      (interviewer_email, day, start, end))
                    c.execute("UPDATE interviewers SET availability_filled=1 WHERE email=?", (interviewer_email,))
                    conn.commit()
                    st.success("Availability submitted successfully!")
        else:
            st.error("Invalid token. Please check your link.")
    else:
        st.warning("No token found in URL. Please check the email link.")

