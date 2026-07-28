import streamlit as st
# streamlit: web based app making
# light python framrwork 

st.title("AI Resume Maker")

st.markdown("""## User can create or
download AI created Resume based on high ATS
Score""")

#==================AGENT CODE================
# Step 2: Load Modules
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader
from PIL import Image

# ===========API KEY LOAD=================

GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE_API_KEY",type="password")
GROQ_API_KEY = st.sidebar.text_input("GROQ_API_KEY",type="password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API_KEY",type="password")

if not (GOOGLE_API_KEY) and not (GROQ_API_KEY) and not (TAVILY_API_KEY):
    st.sidebar.warning("Pass API Keys")
    st.stop()
else:
    st.success("API Keys Loaded")

#==========MODEL BUILDING===============
model = ChatGoogleGenerativeAI(
    model = 'gemini-3.5-flash-lite',
    google_api_key = GOOGLE_API_KEY
)

def search_recent_news_jobs(query):
  """This function helps to search
  recent news or recent jobs
  related to given search query
  suppose user write Python Developer Jobs
  I tshould retuen trending news and jobs link"""
  client  = TavilyClient (
    api_key = TAVILY_API_KEY)
  return client.search(query)

# Agent creation
from langchain.agents import create_agent

agent = create_agent(
    model = model,
    tools = [search_recent_news_jobs]
)

# =========PROMPT GENERATOR=================

def prompt_generator(agent):
  """This function help to ive detailed prompt
  followed br Chain of thoughts and
  persona based prompting, main task is to give
  detailed prompt to build Resume for
  Students or Experirnced person
  Based on their personal information.
  """

  prompt = """You are a Senior HR reume Analyzer,
  main task is to give
  detailed prompt to build Resume for
  Students or Experirnced person
  Based on their personal information.
  System Instruction I want Model to generate resume
  in HTML format, include that in prompt"""

  response = agent.invoke(prompt)
  file_name = 'prompt.py'
  with open(file_name, 'w') as f:
    f.write(response.content[-1]['text'])
  return "Prompt file generated Successfully, agent can read it"
prompt_generator(model)
# tool 2:
def resume_maker_prompt():
  """This function just gives
  updated prompt for model"""

  with open('prompt.py', 'r') as f:
    prompt = f.read()
  return prompt
resume_maker_prompt()


# ===============UPLOAD IMAGE======================
uploaded_file = st.sidebar.file_uploader(
    "Choose an image file",
    type=["jpg","jpeg","png","webp"]
)
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        base_name = os.path.splitext(uploaded_file.name) [0]
        save_path = f"{base_name}.jpg"

        # 3. Save the image to the current working directory
        image.save(save_path, "JPEG")
        st.sidebar.success (f" Image successfully saved as `{save_path}'`!")
    except Exception as e:
        st.error(f"Error processing image: {e}")

# ===========RESUME GENERATOR======================
prompt = """Your are a helpful AI assistant
with job resume maker, your task is to give
HTML format resume, with proper designing using recent CSS and JS
code, with professional design Format.
User will upload data and return HTML format resume
"""  # Use different color or styling
final_prompt = prompt + resume_maker_prompt()

user_info = st.text_input("Enter your information")
user_details = f"""user details: given below:
Resume info: {user_info}
Photo: {uploaded_file }
Photo present ub current directory with name as
uploaded_file, and once resume generated give
dowload button in same html code.
Default if not given: Give Python Developer Resume"""

user_details = """User details: given below:
Give Python Developer Resume
Saksham Solanki
City: New Delhi
State: Delhi
number: +91 8448660717
email_id: saksham.14solanki@gmail.com
**Professional Summary**
**Professional Summary**

Motivated and detail-oriented Bachelor of Computer Applications (BCA) student at IINTM Janakpuri with a strong foundation in programming, database management, and web technologies. Passionate about learning emerging technologies and applying technical knowledge to solve real-world problems. Possesses good analytical, problem-solving, and communication skills, with the ability to work effectively both independently and as part of a team. Eager to gain practical experience through internships and contribute to organizational growth while continuously enhancing technical and professional skills.


**Technical Skills**

* **Programming Languages:** C, C++, Java, Python (Basic)
* **Web Technologies:** HTML5, CSS3, JavaScript, Bootstrap
* **Database Management:** MySQL, SQL
* **Development Tools:** Visual Studio Code, Eclipse, NetBeans
* **Version Control:** Git, GitHub (Basic)
* **Operating Systems:** Windows, Linux (Basic)
* **Microsoft Office:** Word, Excel, PowerPoint
* **Core Concepts:** Object-Oriented Programming (OOP), Data Structures, Database Management System (DBMS), Operating Systems, Computer Networks


"""

query = final_prompt + user_details

if st.button("Generate Resume"):
  with st.spinner("Running Agent...."):
    
    response = agent.invoke({'messages':[{'role':'user',
                                        "content":query}]})
    code = response['messages'][-1].content[-1]['text']

    # st.markdown(code)
    st.html(code, width = "stretch", unsafe_allow_javascript=True)
    
