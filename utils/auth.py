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

def encrypt_password(password: str) -> str:
    """
    Encrypts the string using bcrypt
    
    --------
    Parameters
    password: str
        Containing the user provided password to encrypt.
    
    --------
    Returns
        str containing the new encrypted password
    """
    return bcrypt_context.hash(password)

def register_user(
    username: str,
    password: str,
    password2: str,
    first_name: str,
    last_name: str,
    e_mail: str,
    db: SessionLocal = next(get_db())) -> None:

    """
    Takes the user provided information and sends it to the database as a registered user
    
    --------
    Parameters
    username: str
        Containing the username (provided by the user)
    password: str
        Containing the password (provided by the user)
    password2: str
        Containing the validated password (provided by the user)
    first_name: str
        Containing the user's first name (provided by the user)
    last_name: str
        Containing the user's last name (provided by the user)
    e_mail: str
        Containing the user's email (provided by the user)
    db: sqlalchemy.orm.sessionmaker
        Session which will be commited to the database containg the user provided information
    """

    #Validates that no entry is empty
    for variable in (username, password, first_name, e_mail):
        if variable == "":
            return st.error("Please provide value in all fields")
    
    #Strips whitespace
    username, e_mail = username.strip(), e_mail.strip()

    #Checks if the username or email already exists in the database.
    validation1 = db.query(models.Users).filter(models.Users.username == username).first()
    validation2 = db.query(models.Users).filter(models.Users.email == e_mail).first()

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
    Helper function to authenticate_user()
    Checking whether the plain text password matches the encrypted password using the encryption algorithm
    
    --------
    Parameters
    plain_password: str
        Plain text password
    hashed_password: str
        Encrypted password
    
    --------
    Returns
    Boolean if password matches or not
    """

    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username: str , password: str, db: SessionLocal) -> dict:
    """
    Helper function to login()
    Authenticates the user provided information in the login section.
    Checks that the user exists and that the password is correct
    

    username: str
        Containing the username (provided by the user).
    password: str
        Containing the plain text passwword (provided by the user).
    db: sqlalchemy.orm.sessionmaker
        Containing the session from which the database will be called.
    
    --------
    Returns
    user: dict
        Containing user information from the database.
    """

    #Checks that username exists in database.
    user = db.query(models.Users).filter(models.Users.username == username).first()

    #Returns the user if encrypted password matches the plain textpassword
    if user and verify_password(password, user.hashed_password):
        return user
    
    return None

def login(username: str, password: str, db: SessionLocal = next(get_db())) -> st.session_state:
    """
    Calls the database and validates the provided login information.
    Used to achieve statefullness within the application

    --------
    Parameters
    username: str
        Containing the username (provided by the user).
    password: str
        Containing the plain text passwword (provided by the user).
    db: sqlalchemy.orm.sessionmaker
        Containing the session from which the database will be called.
    
    --------
    Returns
    st.session.state containing the current user, the user's first name and the user id.
    """
    
    user = authenticate_user(username, password, db)

    if not user:
        st.error("Invalid credentials!")
        return st.stop()

    st.session_state["current_user"] = user.username
    st.session_state["first_name"] = user.first_name
    st.session_state["user_id"] = user.user_id

    return st.session_state["current_user"], st.session_state["first_name"], st.session_state["user_id"]