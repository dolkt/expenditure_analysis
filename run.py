from database import engine, SessionLocal
from passlib.context import CryptContext
import models
import utils
import streamlit as st
import streamlit_authenticator as stauth

models.Base.metadata.create_all(bind=engine)

#<<<----Register user>>-----

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally: 
        db.close()


if "current_user" not in st.session_state:
#<<<----Login>>-----
    st.subheader("Login")

    login_username = st.text_input(label="Username", key="login_username")
    login_password = st.text_input(label="Password", type="password", key="login_password")

    st.button(label="Login", key="log_in", on_click=utils.login, args=(login_username, login_password))

#<<<----Register user>>-----
    with st.expander(label="Register"):
        col1, col2  = st.columns(2)

        with col1:
            provided_username = st.text_input(label="Username")
            provided_password = st.text_input(label="Password", type="password")
            provided_password2 = st.text_input(label="Repeat password", type="password")

        with col2: 
            provided_fname = st.text_input("First name")
            provided_lname = st.text_input("Last name")
            provided_email = st.text_input("E-mail")
            user_registration = st.button("Register", on_click=utils.register_user, key="register", args=(provided_username, provided_password, provided_password2, provided_fname, provided_lname, provided_email))
            

else:
    st.sidebar.title(f"Välkommen {st.session_state['first_name']}")



st.session_state


