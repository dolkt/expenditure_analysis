from database import engine, SessionLocal
from passlib.context import CryptContext
import models
import streamlit as st

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally: 
        db.close()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encrypt_password(password: str):
    return bcrypt_context.hash(password)

def register_user(
    username: str,
    password: str,
    password2: str,
    first_name: str,
    last_name: str,
    e_mail: str,
    db: SessionLocal = next(get_db())):

    for variable in (username, password, first_name, e_mail):
        if variable == "":
            return st.error("Please provide value in all fields")

    validation1 = db.query(models.Users).filter(models.Users.username == username).first()
    validation2 = db.query(models.Users).filter(models.Users.email == e_mail). first()

    if validation1 is not None:
        return st.error("User with that name already exists")
    if validation2 is not None:
        return st.error("User already registered to that e-mail")
    if password != password2:
        return st.error("Passwords do not match!")
    
    user_model = models.Users()

    user_model.username = username
    user_model.hashed_password = encrypt_password(password)
    user_model.first_name = first_name
    user_model.last_name = last_name
    user_model.email = e_mail


    db.add(user_model)
    db.commit()

    return st.success("User was added!")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checking whether the plain text password matches the encrypted password using the encryption algorithm
    
    ------
    Parameters
    plain_password: str of plain text password
    hashed_password: str of encrypted password
    
    ------
    Returns
    Boolean if password matches or not
    """

    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username: str , password: str, db) -> dict:

    user = db.query(models.Users).filter(models.Users.username == username).first()

    if user and verify_password(password, user.hashed_password):
        return user
    
    return None

def login(username: str, password: str, db: SessionLocal = next(get_db())):
    #Todo 
    #Query db to get username, encrypted_password and name of user. Load it into stauth.authenticate.
    #If user does not exist return st.error.
    #Check article in "to read" in Chrome
    
    user = authenticate_user(username, password, db)

    if not user:
        st.error("Invalid credentials!")
        return st.stop()

    st.session_state["current_user"] = user.username
    st.session_state["first_name"] = user.first_name
    st.session_state["user_id"] = user.user_id

    return st.session_state["current_user"], st.session_state["first_name"], st.session_state["user_id"]