import streamlit as st
import db

def candidate_form():
    st.title("Candidate Slot Booking")
    email = st.text_input("Enter your email:")

    slots = db.get_available_slots()

    if not slots:
        st.info("No available slots currently.")
        return
    
    options = {f"{s[2]} {s[3]}-{s[4]} (Interviewer: {s[1]})": s[0] for s in slots}
    choice = st.selectbox("Pick a slot", list(options.keys()))

    if st.button("Book Slot"):
        selected_slot_id = options[choice]
        db.book_slot(email, selected_slot_id)
        details = db.get_booking_details(email)
        st.success(f"Booking confirmed with {details[0]} on {details[1]} from {details[2]} to {details[3]}.")
