import streamlit as st
import os
from io import BytesIO
from base64 import b64encode
from PIL import Image
import anthropic
import google.generativeai as genai

claude_api_key = os.environ['CLAUDE_API_KEY']
gemini_api_key = os.environ['GEMINI_API_KEY']
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-pro')

st.title("Take a picture of what's inside your fridge and get five recipes")
img_file = st.camera_input('')

if img_file is not None:
    img = Image.open(img_file)
    buffered = BytesIO()
    img.save(buffered, format='jpeg')
    img_data = b64encode(buffered.getvalue()).decode('utf-8')

    with st.spinner('Working on the classification of the objects in the photo and generating a recipes'):
        message = anthropic.Anthropic(api_key=claude_api_key).messages.create(
            model='claude-3-opus-20240229',
            max_tokens=2048,
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Extract only a list of various food visible in this photo. List only the food separated by comma.'
                        },
                        {
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/jpeg',
                                'data': img_data,
                            },
                        }

                    ],
                }
            ],
        )

        food = message.content[0].text
        st.markdown(f'Claude 3 Opus model detects next food in your fridge: {food}.')
        recipes = gemini_model.generate_content(f'Suggest 5 recipes for this food list: {food}.')

    st.divider()
    st.markdown('Here are 5 recipes for you from Gemini-Pro model.')
    st.markdown(recipes.text)