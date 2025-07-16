import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os

os.environ["GOOGLE_API_KEY"] = "enter_your_api"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Ariyaani-Here", layout="centered")
st.title("Web-Scraping using Gemini AI")

url = st.text_input("Website URL", placeholder="https://example.com")
question = st.text_area("Your Question", placeholder="What is this website about?", height=100)

if st.button("Ask Me Dude"):
    if not url or not question:
        st.warning("Please fill in both the URL and your question.")
    else:
        try:
            with st.spinner("Scraping website content..."):
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                if len(text) == 0:
                    st.error("No content found on the page.")
                    st.stop()

            content_to_send = text[:15000]

            with st.spinner("Sending to Gemini AI..."):
                prompt = f"You are given the following website content:\n\n{content_to_send}\n\nNow answer this question:\n{question}"
                result = model.generate_content(prompt)

            st.success("Gemini AI's Response:")
            st.write(result.text)

        except Exception as e:
            st.error(f" Error: {str(e)}")
