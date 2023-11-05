import os
import time

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

openaikey = st.secrets["openaikey"]
supabase_url = st.secrets["supabase_url"]
supabase_key = st.secrets["supabase_key"]

## Set Environment Variables ##
supabase: Client = create_client(supabase_url, supabase_key)
os.environ['OPENAI_API_KEY'] = openaikey

useraikey = st.sidebar("Enter your OpenAI API Key")

financial_topics = ["Saving Money", "Budgeting", "Tax", "Investing"]
banking_topics = ["Banking Services", "Saving Accounts", "Debit & Credit Cards"]
e_safety_topics = ["Online Banking", "Phishing", "Gambling",]

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

    story_chunks = story.split("#NEWFRAME")
    story_chunks = [chunk.strip() for chunk in story_chunks if chunk.strip()]
    full_story = " ".join(story_chunks)
    title = story_title(full_story)
    
    image_desc = image_description(story_chunks[0], art_style)
    
    # Push to data to Supabase
    newStory = supabase.table("Stories").insert({"story_title": title,}).execute()
    story_id = newStory.data[0]["story_id"]
    newFrame = supabase.table("Frames").insert({"frame_no": 1, "frame_text": story_chunks[0], "story_id": story_id}).execute()
    frame_id = newFrame.data[0]["frame_id"]

    # Generate Image
    
    response = openai.Image.create(
    prompt=image_desc,
    n=1,
    size="256x256",
    response_format = "b64_json"
    )

    #decode image
    b64_image = response['data'][0]['b64_json']
    b64_image_data = b64decode(b64_image)

    # upload image to supabase
    upload_response = supabase.storage.from_("images").upload(
    file=b64_image_data,
    path=f"{story_id}.{frame_id}.1.png",
    file_options={"content-type": "image/png"}
    )
    
    #Get link to image
    get_img_url = supabase.storage.from_("images").create_signed_url(f"{story_id}.{frame_id}.1.png", 600)  # 60 is the number of seconds the URL will be valid for.
  
  st.divider()

  #Display image to webpage
  st.markdown(f"![Alt Text]({get_img_url['signedURL']})")
  st.write("-")
  st.write(story_chunks[0])

  for i in range(1, 10):
    with st.spinner("Loading next page"):
      #Add new frame to frames DB
      newFrame = supabase.table("Frames").insert({"frame_no": (i+1), "frame_text": story_chunks[i], "story_id": story_id}).execute()

      #find frame_id
      frame_id = newFrame.data[0]["frame_id"]
      frame_no = i+1

      #generate image description
      image_desc = image_description(story_chunks[i], art_style)
      
      #generate image
      response = openai.Image.create(
      prompt=image_desc,
      n=1,
      size="256x256",
      response_format = "b64_json"
      )

      time.sleep(12)

      #decode image
      b64_image = response['data'][0]['b64_json']
      b64_image_data = b64decode(b64_image)

      # upload image to supabase
      upload_response = supabase.storage.from_("images").upload(
      file=b64_image_data,      
      path=f"{story_id}.{frame_id}.{frame_no}.png",
      file_options={"content-type": "image/png"}
      )
      
      #Get link to image
      get_img_url = supabase.storage.from_("images").create_signed_url(f"{story_id}.{frame_id}.{frame_no}.png", 600)  # 60 is the number of seconds the URL will be valid for.

    st.divider()
    
    #Display image to webpage
    st.markdown(f"![Alt Text]({get_img_url['signedURL']})")
    st.write("-")
    st.write(story_chunks[i])






