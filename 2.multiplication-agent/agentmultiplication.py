# AIzaSyCOvg-NdRrPbK1wNXxU9XQGEYJkoCEeIYI
import os
import streamlit as st
from langchain.agents import tool, initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI

# 🔐 Set your Google API Key
os.environ["GOOGLE_API_KEY"] = "enter_your_api"

# 🔮 Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

# 🛠️ Define a tool
@tool
def lwmul(x: str) -> str:
    """
    Multiplies the given number by 4.
    Accepts input as a string, converts to integer, and returns the result.
    """
    try:
        num = int(x)
        return str(num * 4)
    except ValueError:
        return "Invalid input. Please provide an integer."

tools = [lwmul]

# 🤖 Initialize the agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# 🌐 Streamlit UI
st.set_page_config(page_title="LangChain Agent Demo", layout="centered")
st.title("🔗 LangChain Agent with Gemini")

user_input = st.text_input("Enter your request (e.g., 'can you plz give me output with input of 8')")

if st.button("Get Result"):
    if user_input:
        with st.spinner("Agent is thinking..."):
            try:
                result = agent.run(user_input)
                st.success("✅ Output:")
                st.code(result)
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning("Please enter some input to proceed.")
