import streamlit as st
import pandas as pd
import utils
import database
import models


#Setting the title for the page as well as the icon displayed in the browser tab
st.set_page_config(page_title="Upload Data", page_icon="💾")


#Header for the page
st.subheader("Upload Data by File")

#File upload functionality. Restricted to .xls.
chosen_file = st.file_uploader(label="Choose a file", help="Select a transactionfile from Handelsbanken",
                                type="xls")

#Stops the page if no file is uploaded
if chosen_file:
    #Reads the user provided xls.
    df = pd.read_html(chosen_file)[3] 

    #Categorizes the costs based on the parameters in the categorization function
    df = utils.categorization(df, user_id=st.session_state["user_id"])

    #Shows sample data from the provided xls.
    st.write("Sample from the data to upload:", df.head())

    df["user_id"] = st.session_state["user_id"]

    #Prompts the user whether they want to upload the data to the database
    upload_prompt = st.button("Upload to database?", key="file_upload")

#If upload is selected it checks db for the latest provided date and masks
#the provided file from that date.
    if upload_prompt:

        date_checker = database.check_latest_date(user_id=st.session_state["user_id"])
        
        df = df[df["Transaktionsdatum"] > date_checker]

        if len(df) > 1:
            #database.upload_data(df)
            df.to_sql(con=database.engine, name=models.Expenditures.__tablename__, if_exists="append", index=False)
            st.success("Data was uploaded", icon="✔")
        else:
            st.error("All that data is already in the database")
         



st.subheader("Upload Data Manually")

col1, col2 = st.columns(2)

manual_expenditure = pd.DataFrame(columns=["Transaktionsdatum", "Text", "Belopp", "Typ", "Kategori"])
if "expend_df" not in st.session_state:
        st.session_state["expend_df"] = manual_expenditure


with col1:
    expenditure_form = st.form("expenditure_form", clear_on_submit=True)
    
    expenditure_form.subheader("Add expenditure")
    expenditure_amount = expenditure_form.number_input("Amount", step=int(1))
    expenditure_category = expenditure_form.selectbox("Category", options=database.get_user_categories(st.session_state["user_id"], usage="display")["Name"].unique())
    expenditure_date = expenditure_form.date_input("Date")
    expenditure_text = expenditure_form.text_input("Add text (Optional)")

    expenditure_submit = expenditure_form.form_submit_button("Add expenditure")

if expenditure_submit:
    new_data = utils.add_expenditure(
        date = expenditure_date,
        category = expenditure_category,
        amount = expenditure_amount,
        user_id = st.session_state["user_id"],
        text = expenditure_text
    )

    #Ändra så att den hämtar nya dataframes från add expenditure och lägger till i session state istället.
    st.session_state["expend_df"] = pd.concat([st.session_state["expend_df"], new_data], ignore_index=True)


with col2:
    if len(st.session_state["expend_df"]) == 0:
        st.empty()
    else:
        st.session_state["expend_df"]
    
        manual_upload = st.button("Upload to database?", key="manual_expenditure")

        if manual_upload:
            st.session_state["expend_df"].to_sql(con=database.engine,name=models.Expenditures.__tablename__, if_exists="append", index=False)
            del st.session_state["expend_df"]
            st.success("Data was uploaded!")
            


st.session_state