import streamlit as st
import database
import utils

#Sets the page configuration so that the browser shows the page name and icon.
st.set_page_config("💰 Categories Setup", page_icon="💰")

#<<<----Initial informational section>>>----
if "current_user" in st.session_state:
    st.subheader("User Categories")
    st.markdown("In this section you will be able to configure the categories that will be used for your expenditure categorization. The page consists of three sub-pages:  \n"
                "* **Add Category** - Here you can add new categories to categorize your expenditures.  \n"
                "* **Identify Category by Text** - This is used if you are using file upload for your expenditures. It automatically categorizes your expenditures based on the text.  \n"
                "* **Delete Category** - Here you can delete your categories.")

    #Retrieves the user's categories from the database.
    user_categories = database.get_user_categories(user_id=st.session_state["user_id"], usage="display")

    #<<<----Expander to show the user's categories>>>----
    with st.expander("Show my categories"):
        if len(user_categories) != 0:
            st.caption(":red[Note:] :pencil: A category will appear multiple times if you are using different texts to identify it.  \n"
                    "The different identifying texts are used for automatic categorization via file upload")
            st.dataframe(user_categories, use_container_width=True)
        else:
            st.warning("You do not have any categories yet!")


    #<<<----Add, edit or delete a category section>>>----
    st.subheader("Add, Identify or Delete a Category")

    add_tab, edit_tab, delete_tab = st.tabs(["Add Category", "Identify Category by Text", "Delete Category"])

    #Sends the added category to the database and places the current user as the owner of that category.
    with add_tab:
        category_name = st.text_input("Category Name")
        category_text = st.text_input("Text that identifies your category (Optional)", help="This is used if you upload files containing your expenditures. It automates categorization of your expenditures")
        add_category = st.button(
            "Add Category", 
            key="add_category", 
            on_click=utils.add_category, 
            kwargs={"user_id": st.session_state["user_id"], "category_name": category_name, "category_text": category_text})

    with edit_tab:
        
        col1, col2 = st.columns(2)
        
        #Updates the entries with the user provided text as well as adds an additional category row for that identifying text for the given category.
        with col1:
            st.caption(":red[Note:] :pencil: This functionality is for when you upload your expenditures via file upload.  \n"
                    "The expenditures will be automatically categorized given the identifying text you provide.")
            existing_category = st.selectbox("Category", options=user_categories["Name"].unique())
            identifying_text = st.text_input("Text that identifies your category")
            customize_category = st.button(
                "Update Category",
                key="update_category",
                on_click=utils.update_category,
                kwargs={"user_id": st.session_state["user_id"], "category_name": existing_category, "category_text": identifying_text})
        
        #Retrieves all the uncategorized expenditures for the given user.
        with col2:
            st.caption("Here are your expenditures which could not be categorized automatically.  \n"
                    "The table shows the amount of **:blue[occurances]** for the given text and the **:blue[amount]** spent. \n"
                    "Copy the value in **:blue[Text]** from the table and paste it into **:blue['Text that identifies your category']**")
            st.write(database.get_uncategorized(user_id=st.session_state["user_id"]))

    #Deletes the category for the given user and puts all the expenditures within that category as uncategorized.
    with delete_tab:
        st.caption(":red[Note:] :pencil: All your expenditures within the deleted category will be put as uncategorized.  \n"
                    "You can choose to recategorize them in the :blue['Identify Category by Text'] tab.")
        category_to_delete = st.selectbox(
            "Category to delete",
            options=user_categories["Name"].unique(),
            key="select_delete")
        st.button("Delete Category",
            key="category_delete",
            on_click=utils.delete_category,
            kwargs={"category_name": category_to_delete, "user_id": st.session_state["user_id"]})

else:
    st.warning("Log in to your account to view this section")
