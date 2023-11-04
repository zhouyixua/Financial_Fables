import streamlit as st
import os

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from apikeys import openaikey

os.environ['OPENAI_API_KEY'] = openaikey

financial_topics = ["Saving Money", "Budgeting", "Tax", "Compound Interest", "Investing"]
banking_topics = ["Banking Services", "Saving Accounts", ]
e_safety_topics = ["Online Banking", "Phishing", "Gambling"]

st.title("New Story 📗")
user_age = st.text_input("How old are you?")
main_char = st.text_input("What's the name of your main character?")
mchar_description = st.text_input("Describe your main character:")
overall_topic = st.selectbox("What area would you like to learn about?", ["-", "Finances", "Banking", "E-Safety"])

topics = ["Please select an overall topic"]

if overall_topic == "Finances":
  topics = financial_topics
elif overall_topic == "Banking":
  topics = banking_topics
elif overall_topic == "E-Safety":
  topics = e_safety_topics

topic_choice = st.selectbox("What topic would you like to learn about?", topics)

generate = st.button("Generate")

def generate_story(age, charname, char_descript, topic):
    chat = ChatOpenAI(temperature=0.7, model="gpt-4") # Here temperature is set to temp to provide a balanced response

    template = """
        You are a educational story writer for children. Your job is to write short stories which teach financial literacy. You should always use positive language.
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = f""""
      Write a 10 frame childrens story about {topic}. The target audience is a child aged {age}.
      The main character of the story will be called {charname}. Here is a description of the main character: {char_descript}. Each frame should start with #NEWFRAME 
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run({"age": age, "charname": charname, "char_descript": char_descript, "topic": topic})
    return result

if generate:
  with st.spinner("Generating your story"):
    story = generate_story(user_age, main_char, mchar_description, topic_choice)
    story_chunks = story.split("#NEWFRAME")
    story_chunks = [chunk.strip() for chunk in story_chunks if chunk.strip()]
  st.divider()

  st.write(story)


