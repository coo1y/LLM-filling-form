import base64
from typing import Generator
import streamlit as st
from streamlit_chat import message
from streamlit_javascript import st_javascript
import llm
from gtts import gTTS
from pygame import mixer
import subprocess

uploaded_file = "data/i-765_decrypt (1).pdf"

st.set_page_config(page_title="PDF form filling", page_icon="📖", layout="wide")
st.header("I-765 Form Filling")

together_api_key = st.text_input("Insert Together API Key for Llama", type="password")

def create_new_template():
    # clear data cache
    st.cache_data.clear()

    # create new I765 template
    subprocess.call(['sh', './new_template.sh'])

def displayPDF(pdf_name, width):
    # Read file as bytes:
    with open(pdf_name, "rb") as pdf_file:
        bytes_data = pdf_file.read()

    # Convert to utf-8
    base64_pdf = base64.b64encode(bytes_data).decode("utf-8", 'ignore')

    # Embed PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width={str(width)} height={str(width*4/3)} type="application/pdf"></iframe>'

    # Display file
    st.markdown(pdf_display, unsafe_allow_html=True)

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

if together_api_key:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("Welcome. I am an AI immigration officer. I am here to help you fill the I-765 form you want.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask the AI 🤖"):
        st.session_state.messages.append({"role": "user", "avatar": "👨‍💻", "content": prompt})
        with st.chat_message("user", avatar="👨‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("The AI is thinking..."):
                stream = llm.reply_prompt(
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    together_api_key=together_api_key,
                )
                
            chat_responses_generator = generate_chat_responses(stream)
            response = st.write_stream(chat_responses_generator)

        st.session_state.messages.append({"role": "assistant", "avatar": "🤖", "content": response})

        # speak = gTTS(text=response, slow=False)
        # audio_file_name = "audio/captured_voice.mp3"
        # speak.save(audio_file_name)
        # mixer.init()
        # mixer.music.load(audio_file_name)
        # mixer.music.play()

# clear data cache
st.cache_data.clear()

with st.sidebar:
    st.button('New I-765 Form', on_click=create_new_template)

    if uploaded_file:
        ui_width = st_javascript("window.innerWidth")
        displayPDF(uploaded_file, ui_width)

# clear data cache
st.cache_data.clear()
