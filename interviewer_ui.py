import streamlit as st
import db

def interviewer_form(token):
    email_record = db.get_interviewer_by_token(token)
    if not email_record:
        st.error("Invalid or expired link.")
        return
    
    email = email_record[0]
    st.title("Set Your Weekly Availability")

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    availability = []

    for day in days:
        with st.expander(day):
            start_time = st.time_input(f"{day} Start Time", key=f"{day}_start")
            end_time = st.time_input(f"{day} End Time", key=f"{day}_end")
            availability.append((day, start_time.strftime("%H:%M"), end_time.strftime("%H:%M")))

    if st.button("Submit Availability"):
        db.save_availability(email, availability)
        db.mark_availability_filled(email)
        st.success("Availability saved successfully!")
