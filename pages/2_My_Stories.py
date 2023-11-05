import streamlit as st
from supabase import create_client, Client

supabase_url = st.secrets["supabase_url"]
supabase_key = st.secrets["supabase_key"]

supabase: Client = create_client(supabase_url, supabase_key)

story_data = supabase.table('Stories').select("story_id", "story_title").execute()

story_titles = []

for story in story_data.data:
  story_title = story["story_title"]
  story_titles.append(story_title)

st.title("My Stories")
story_choice = st.selectbox("Which of your stories would you like to read?", story_titles)
load = st.button("Load Story")

if load:
  current_story = story_choice
  for story in story_data.data:
    if current_story == story["story_title"]:
      story_id = story["story_id"]
  frame_data = supabase.table('Frames').select("*").eq("story_id", story_id).execute()
  frames = frame_data.data

  for i in range(0, 10):
    frame_id = frames[i]["frame_id"]
    frame_no = (i+1)
    get_img_url = supabase.storage.from_("images").create_signed_url(f"{story_id}.{frame_id}.{frame_no}.png", 600)  # 60 is the number of seconds the URL will be valid for.
    col1, col2, col3 = st.columns(3)
    with col2:
      st.markdown(f"![Alt Text]({get_img_url['signedURL']})")
    st.write(frames[i]["frame_text"])
