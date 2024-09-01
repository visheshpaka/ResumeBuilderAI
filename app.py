from langchain_huggingface import HuggingFaceEndpoint  # Import Hugging Face endpoint class
from secret_api_keys import hugging_face_api_key # Import secret API key from separate file
from langchain.prompts import PromptTemplate  # Import PromptTemplate class from langchain

import os  # Import the 'os' module for potential system interactions
import streamlit as st  # Import Streamlit for web app development

# Set the Hugging Face Hub API token as an environment variable
os.environ['HUGGINGFACEHUB_API_TOKEN'] = hugging_face_api_key

# Define the Hugging Face model repository ID
repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Create a Hugging Face Endpoint instance
llm = HuggingFaceEndpoint(
    repo_id=repo_id,  # Specify the model repository ID
    temperature=0.6,  # Set the temperature parameter (controls randomness)
    token=hugging_face_api_key,  # Use the API key for authentication
)

# Define a PromptTemplate for resume section suggestions
prompt_template_for_resume_sections = PromptTemplate(
    input_variables=['job_title', 'skills', 'experience_level'],  # Specify input variables
    template=  # Define the prompt template
    '''
    I'm building a professional resume for a "{job_title}" role.
    The candidate's experience level is "{experience_level}", and they have the following skills: {skills}.
    Based on this information, suggest a detailed resume section outline, including an objective, experience, skills, and additional sections.
    '''
)

resume_section_chain = prompt_template_for_resume_sections | llm  # Define the resume section generation chain

## Working on UI with the help of streamlit
st.title("💼 SmartResume AI 💼")
st.header("Build a Professional Resume with AI Assistance")

# Ensure session state initialization
if 'job_title' not in st.session_state:
    st.session_state['job_title'] = ""
if 'skills' not in st.session_state:
    st.session_state['skills'] = []
if 'experience_level' not in st.session_state:
    st.session_state['experience_level'] = "Beginner"  # Set default experience level to 'Beginner'
if 'sections' not in st.session_state:
    st.session_state['sections'] = ""
if 'resume_format' not in st.session_state:
    st.session_state['resume_format'] = "Chronological"  # Default resume format

# Resume Section Generation
st.subheader('Resume Section Suggestion')
job_expander = st.expander("Input Job Details")

with job_expander:
    st.session_state['job_title'] = st.text_input("Job Title", value=st.session_state['job_title'])

    # Fix for experience level selectbox
    st.session_state['experience_level'] = st.selectbox(
        'Experience Level:',
        ['Beginner', 'Intermediate', 'Expert'],
        index=['Beginner', 'Intermediate', 'Expert'].index(st.session_state['experience_level'])  # Ensure the session state value is valid
    )

    # Skill input and management
    skills_input = st.text_input("Enter a Skill:")
    add_skill_button = st.button("Add Skill")

    if add_skill_button and skills_input:
        st.session_state['skills'].append(skills_input.strip())
        skills_input = ""  # Clear the input field after adding a skill

    if st.session_state['skills']:
        st.write("Skills added:")
        cols = st.columns(4)  # Display 4 skills per row
        for i, skill in enumerate(st.session_state['skills']):
            with cols[i % 4]:
                st.write(f"<div style='display: inline-block; background-color: lightgray; padding: 5px; margin: 5px;'>{skill}</div>", unsafe_allow_html=True)
                if st.button(f'Remove {skill}', key=f'remove_{i}'):
                    st.session_state['skills'].remove(skill)

    submit_job_info = st.button('Submit Job Info')

# When job info is submitted
if submit_job_info:
    formatted_skills = ', '.join(st.session_state['skills'])

    if not st.session_state['job_title']:
        st.warning('Please enter a job title before generating the resume sections.')
    else:
        st.subheader(f"Resume Sections for {st.session_state['job_title']}")
        with st.spinner("Generating resume sections..."):
            resume_sections = resume_section_chain.invoke({
                'job_title': st.session_state['job_title'],
                'skills': formatted_skills,
                'experience_level': st.session_state['experience_level']
            })
        st.write(resume_sections)

# Resume Format Selection
st.subheader("Resume Format")
resume_format = st.selectbox(
    "Choose a resume format:",
    ['Chronological', 'Functional', 'Hybrid'],
    index=['Chronological', 'Functional', 'Hybrid'].index(st.session_state['resume_format'])
)

st.write(f"You've selected the {resume_format} resume format.")

