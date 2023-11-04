import streamlit as st

financial_topics = ["Saving Money", "Budgeting", "Tax", "Compound Interest", "Investing"]
banking_topics = ["Banking Services", "Saving Accounts", "Credit & Debit Cards"]
e_safety_topics = ["Online Banking", "Phishing", "Gambling"]

#### FRONT END ####

st.title("Financial Fables 💰")

st.write("This is an app to help you learn more about finances, banking, e-safety and being a grown up.")

st.subheader("Here are the topics you can learn about:")

col1, col2, col3 = st.columns(3)

with col1:
  st.subheader("Finances")
  for topic in financial_topics:
    st.write(topic)

with col2:
  st.subheader("Banking")
  for topic in banking_topics:
    st.write(topic)

with col3:
  st.subheader("E-safety")
  for topic in e_safety_topics:
    st.write(topic)

st.write("To find out more about these topics, create a new story")
