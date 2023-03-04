import streamlit as st
import database
import utils
import pandas as pd

st.set_page_config("Settings", page_icon="⚙")


st.subheader("User Categories")
st.markdown("""Is this section you will be able to configure the categories that will be used for your expenditure categorization""")


user_categories = database.get_user_categories(user_id=st.session_state["user_id"], usage="cost_categorization")


if len(user_categories) != 0:
    st.subheader("Your categories:")
    user_categories

st.subheader("Handle your Categories")
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
        existing_category = st.selectbox("Category", options=user_categories["name"].unique())
        identifying_text = st.text_input("Text that identifies your category")
        customize_category = st.button(
            "Customize Category",
            key="customize_category",
            on_click=utils.update_category,
            kwargs={"user_id": st.session_state["user_id"], "category_name": existing_category, "category_text": identifying_text}
        )

#Add the customized category to db.

#Try to add into dict
#categories_dict = {}
#for _, row in user_categories.iterrows():
    #if row["name"] not in categories_dict:
        #categories_dict[row["name"]] = [row["text"]]
    #else:
        #categories_dict[row["name"]].append(row["text"])

categories_dict = utils.categories_dict(st.session_state["user_id"])


st.write(categories_dict)
st.write(database.get_uncategorized(user_id=st.session_state["user_id"]))

#st.write(dict(zip(user_categories.name, user_categories.text)))

#st.write(pd.Series(user_categories.text.values, index=user_categories.name.values).to_dict())

