import streamlit as st
import database
import utils


st.set_page_config("Settings", page_icon="⚙")


st.subheader("User Categories")
st.markdown("""Is this section you will be able to configure the categories that will be used for your expenditure categorization""")


user_categories = database.get_user_categories(user_id=st.session_state["user_id"], usage="display")


if len(user_categories) != 0:
    st.subheader("Your categories:")
    st.write(user_categories)

st.subheader("Add or Edit a Category")
col1, col2 = st.columns(2)
with col1:
    with st.expander("Add a new category"):
        category_name = st.text_input("Category Name")
        category_text = st.text_input("Text that identifies your category (Optional)", help="This is used if you upload files containing your expenditures. It automates categorization of your expenditures")
        add_category = st.button(
            "Add Category", 
            key="add_category",
            on_click=utils.add_category,
            kwargs={"user_id": st.session_state["user_id"], "category_name": category_name, "category_text": category_text}
        )

with col2:
    with st.expander("Identify Category by Text"):
        existing_category = st.selectbox("Category", options=user_categories["Name"].unique())
        identifying_text = st.text_input("Text that identifies your category")
        customize_category = st.button(
            "Customize Category",
            key="customize_category",
            on_click=utils.update_category,
            kwargs={"user_id": st.session_state["user_id"], "category_name": existing_category, "category_text": identifying_text}
        )


st.subheader("Deletes")
category_to_delete = st.selectbox(
    "Category to delete", 
    options=user_categories["Name"].unique(),
    key="select_delete"
)
st.button("Delete Category",
          key="category_delete",
          on_click=utils.delete_category,
          kwargs={"category_name": category_to_delete, "user_id": st.session_state["user_id"]})



st.write(database.get_uncategorized(user_id=st.session_state["user_id"]))

#st.write(dict(zip(user_categories.name, user_categories.text)))

#st.write(pd.Series(user_categories.text.values, index=user_categories.name.values).to_dict())

