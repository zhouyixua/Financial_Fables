import os
import time
import io

from base64 import b64decode

# This video explains how to save b64 as file.
# https://www.youtube.com/watch?v=-vFrV1LRhd0

# Store file to Bytes.io, then upload to supabase

import openai
import streamlit as st

from supabase import create_client, Client

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from myapikeys import openaikey, supabase_url, supabase_key

## Set Environment Variables ##
supabase: Client = create_client(supabase_url, supabase_key)
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
art_style = st.selectbox("What illustration style would you like?", ["Manga", "Watercolours", "Comic Book", "3D Animation", "Cartoon", "Psychedelic"])
generate = st.button("Generate")

def generate_story(age, charname, char_descript, topic):
    chat = ChatOpenAI(temperature=0.7, model="gpt-4") # Here temperature is set to temp to provide a balanced response

    template = """
        You are a educational story writer for children's books. Your job is to write short stories which teach financial literacy. You should always use positive and easy to understand language.
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = f""""
      Write a 10 frame childrens story about {topic}. The target audience is a child aged {age}.
      The main character of the story will be called {charname}. Here is a description of the main character: {char_descript}. Each frame should start with '#NEWFRAME'.
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run({"age": age, "charname": charname, "char_descript": char_descript, "topic": topic})
    return result

def image_description(story_chunk, style):
    chat = ChatOpenAI(temperature=0.7, model="gpt-4") # Here temperature is set to temp to provide a balanced response

    template = """
        You are children's book illustrator. Your job is to give a description of an image that would accompany frames from a childrens story.
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = f""""Give a single sentence description of a {style} style illustration that could accompany the following frame from a story: {story_chunk}. Do not include character names or references to other images.

    Example input: Once upon a time, in the bustling city of Taipei, there lived a small girl called Joanne who was always curious about the world. She had an insatiable thirst for knowledge and was specifically intrigued by the concept of money.

    Example output: A {style} style illustration of a small taiwanese girl, standing on a busy street in Taipei.
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run({"story_chunk": story_chunk, "style": style})
    return result

def story_title(full_story):
    chat = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo") # Here temperature is set to temp to provide a balanced response

    template = """
        You are children's book author. Your job is to give a title to stories for children.
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = f""""Give me a title for the following story: {full_story}"""

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run({"full_story": full_story})
    return result


if generate:
  with st.spinner("Generating your story"):
    story = generate_story(user_age, main_char, mchar_description, topic_choice)
    # story = """#NEWFRAME Once upon a time, in the bustling city of Beijing, lived a small, curious boy named Jackie. He was known for his bright, twinkling eyes and his never-ending list of questions.

    # #NEWFRAME One sunny day, Jackie's father took him to a very special place called a bank. Jackie was excited to learn about this new place. His father told him, "Banks are where we keep our money safe, Jackie."

    # #NEWFRAME Inside the bank, Jackie saw people lined up at counters, talking to bank employees. His father explained, "This is called a teller window, Jackie. We can deposit or withdraw money here."

    # #NEWFRAME Jackie's father then showed him a small, plastic card. He explained, "This is called a debit card, we can use it to buy things without carrying cash around. The money comes directly from our bank account."

    # #NEWFRAME Next, they walked over to a machine in the corner of the bank. His father said, "This is an ATM machine, Jackie. It's like a mini bank where we can deposit and withdraw money, even when the bank is closed."

    # #NEWFRAME Jackie then noticed a woman receiving a stack of cash from a bank employee. "That's a loan, Jackie," his father said. "Banks lend money to people for big things like a house or a car. But, we have to pay it back with a little extra, that extra is called interest."

    # #NEWFRAME They then passed by a section where people were happily chatting with bank employees. "These are financial advisors, Jackie. They help people plan how to save and spend their money wisely."

    # #NEWFRAME Jackie's father then showed him a big, metal door. "Behind this door is the bank's safe. It's where the bank keeps everyone's money secure."

    # #NEWFRAME On their way home, Jackie's father opened a small account for Jackie. He explained, "This is your savings account, Jackie. Every time you save money from your pocket change, we can put it here. The bank will even give you a little extra money over time, that's called interest."

    # #NEWFRAME Jackie smiled, feeling very grown-up. He had learned a lot about banks and their services. He couldn't wait to start saving his money in his very own bank account. And that's how our little friend Jackie learned about the world of banking, in a simple, fun and engaging way."""

    story_chunks = story.split("#NEWFRAME")
    story_chunks = [chunk.strip() for chunk in story_chunks if chunk.strip()]
    full_story = " ".join(story_chunks)
    title = story_title(full_story)
    image_desc = image_description(story_chunks[0], art_style)
    newStory = supabase.table("Stories").insert({"story_title": title,}).execute()
    story_id = newStory.data[0]["story_id"]
    newFrame = supabase.table("Frames").insert({"frame_no": 1, "frame_text": story_chunks[0], "story_id": story_id}).execute()
    frame_id = newFrame.data[0]["frame_id"]

    response = openai.Image.create(
    prompt=image_desc,
    n=1,
    size="256x256"
    )

    image_url = response['data'][0]['url'] 

  st.divider()
  st.markdown(f"![Alt Text]({image_url})")
  st.write("-")
  st.write(story_chunks[0])

  for i in range(1, 9):
    with st.spinner("Loading next page"):
      newFrame = supabase.table("Frames").insert({"frame_no": (i+1), "frame_text": story_chunks[i], "story_id": story_id}).execute()
      image_desc = image_description(story_chunks[i], art_style)
      response = openai.Image.create(
      prompt=image_desc,
      n=1,
      size="256x256"
      )
      time.sleep(15)
    image_url = response['data'][0]['url']
    st.divider()
    st.markdown(f"![Alt Text]({image_url})")
    st.write("-")
    st.write(story_chunks[i])






