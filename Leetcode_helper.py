import requests
import json
import streamlit as st
import base64


api_url = "<LAMBDA ENDPOINT URL>"

# Using a screenshot instead
uploaded_file = st.file_uploader("Choose an image ", type = ["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_data = uploaded_file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    print(f'base64_image: {base64_image[:10]}')

    file = json.dumps({'image':base64_image})

    response = requests.post(f'{api_url}', data=file, headers={'Content-Type': 'application/json'})  
    print(f'response: {response}')
    st.write(f'response_body: {response.json()}')





