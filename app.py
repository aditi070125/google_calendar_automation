import streamlit as st
import db
import interviewer_ui
import candidate_ui
import email_utils
import uuid

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["HR Panel", "Interviewer Availability", "Candidate Booking"])

db.create_tables()

if page == "HR Panel":
    st.title("HR Dashboard")
    interviewer_email = st.text_input("Enter Interviewer's Email:")
    
    if st.button("Send Availability Link"):
        token = str(uuid.uuid4())
        db.add_interviewer(interviewer_email, token)
        availability_link = f"http://localhost:8501/?token={token}&page=Interviewer+Availability"
        email_utils.send_email(
            interviewer_email,
            "Set Your Availability",
            f"Hello! Please set your availability here: {availability_link}"
        )
        st.success(f"Email sent to {interviewer_email}")

elif page == "Interviewer Availability":
    query_params = st.experimental_get_query_params()
    token = query_params.get('token', [None])[0]

    if token:
        interviewer_ui.interviewer_form(token)
    else:
        st.error("Missing token. Please check your email link.")

elif page == "Candidate Booking":
    candidate_ui.candidate_form()
