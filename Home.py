from database import engine
import models
import utils
import streamlit as st

models.Base.metadata.create_all(bind=engine)

#Checks if the user is logged in. If not it prompts log-in.
if "current_user" not in st.session_state:

#<<<----Login section>>-----
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
    st.subheader(f"Welcome {st.session_state['first_name']}! 🎉")

    st.markdown("Introducing _:blue[Expenditure Analysis]_ which helps you keep track of your finances.  \n"
                "With this tool, you can visualize your spending over time, allowing you to make informed decisions about your budget and adjust your spending habits as needed.  \n  \n"
                "The application is designed to make tracking your finances :blue[easy and convenient]. You can upload your bank statements directly into the application*, or manually enter your income and expenditures. You can even set up custom categories to label your expenses, so you can easily see where your money is going.  \n  \n"
                "The best part? The application visualizes your spending over time, so you can easily see how your spending habits are changing over months, or years. This information is presented to you in the form of easy-to-read charts and graphs, making it simple to spot trends and identify areas where you might need to cut back.")


    st.subheader("How to use the application")

    st.markdown(
        "1. Begin with setting up your categories.  \n"
        "Click on the :blue['Categories Setup'] section, and then click on :blue['Add Category'] to create a new category.  \n"
        "2. In the :blue['Add Category'] tab, enter a name for your category (e.g. 'Groceries', 'Entertainment', etc).")
    
    st.caption(":red[Note:] :pencil: If you are going to use the File Upload functionality to add expenses/income, make sure you also add :blue['Text that identifies your category'].")

    st.markdown(
        "3. Once you have created your categories, you can start logging your expenses and income.  \n"
        "Click on :blue['Upload Data'] section, and then either upload your transactional data via file or add them manually.  \n"
        "4. You are all set and done!   \n"
        "Your spending will now be visualized, allowing you to keep track of your spending habits in the :blue['Expenditure Visualization'] section.  \n"
        "5. :red[Extra Note]: If you are using file upload and have multiple texts that belongs to a certain category, use the :blue['Identify Category by Text'] tab in :blue['Categories Setup'].  \n"
        "For instance if you have the category 'Subscriptions' where you want Netflix and HBO to be automatically categorized, simply add :green[**Netflix**] and :green[**HBO**] individually in this tab."
    )