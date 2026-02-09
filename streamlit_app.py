import streamlit as st

lab1 = st.Page("Labs/Lab1.py", title = "Lab 1", icon="📝")
lab2 = st.Page("Labs/Lab2.py", title = "Lab 2", icon="📝")
lab3 = st.Page("Labs/Lab3.py", title = "Lab 3", icon="📝")
lab4 = st.Page("Labs/Lab4.py", title = "Lab 4", icon="📝", default=True)

pg = st.navigation([lab1, lab2, lab3, lab4])
st.set_page_config(
   # Set page title
   page_title = "IST 488 Lab App", 
   layout = "wide",
   initial_sidebar_state = "expanded",
   page_icon=":material/edit:"
)
pg.run()
