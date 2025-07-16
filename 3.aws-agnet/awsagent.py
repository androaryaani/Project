import os
import re
import streamlit as st
import boto3
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI

# 🔐 Set Google API Key
os.environ["GOOGLE_API_KEY"] = "enter_your_api"

# 🌐 Streamlit UI
st.set_page_config(page_title="EC2 LangChain Agent", page_icon="🚀")
st.title("🤖 EC2 Instance Automation using LangChain Agent")

# 🧠 Defaults
DEFAULT_INSTANCE_TYPE = "t2.micro"
DEFAULT_REGION = "ap-south-1"
DEFAULT_COUNT = 1

launched_instance_ids = []

# ✅ EC2 Launching Function (AI parsed)
def ec2_launcher_func(prompt: str) -> str:
    global launched_instance_ids

    def clean(val): return val.strip().strip('"').strip("'")

    # Defaults
    instance_type_final = DEFAULT_INSTANCE_TYPE
    region_final = DEFAULT_REGION
    count_final = DEFAULT_COUNT

    try:
        # Extract values from the prompt
        region_match = re.search(r"(?:region|in)\s+([a-z\-0-9]+)", prompt, re.IGNORECASE)
        type_match = re.search(r"(?:type|instance type)\s+([a-z0-9.]+)", prompt, re.IGNORECASE)
        count_match = re.search(r"(?:launch|create|run|spin up)\s+(\d+)", prompt, re.IGNORECASE)

        if region_match:
            region_final = clean(region_match.group(1))
        if type_match:
            instance_type_final = clean(type_match.group(1))
        if count_match:
            count_final = int(count_match.group(1))

        # ✅ Dynamically fetch the latest Amazon Linux 2 AMI
        ssm = boto3.client("ssm", region_name=region_final)
        response = ssm.get_parameter(Name="/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2")
        ami_id = response['Parameter']['Value']

        # 🟢 Launch instance(s)
        ec2 = boto3.resource("ec2", region_name=region_final)
        instances = ec2.create_instances(
            InstanceType=instance_type_final,
            ImageId=ami_id,
            MinCount=1,
            MaxCount=count_final
        )

        output = f"✅ Launched {count_final} EC2 Instance(s):\n\n"
        for instance in instances:
            instance.wait_until_running()
            instance.load()
            launched_instance_ids.append(instance.id)
            output += (
                f"🆔 ID: {instance.id}\n"
                f"🌐 IP: {instance.public_ip_address}\n"
                f"📍 Region: {region_final}\n"
                f"🔁 State: {instance.state['Name']}\n\n"
            )
        return output

    except Exception as e:
        return f"❌ Error launching EC2: {str(e)}"


# ✅ EC2 Termination
def ec2_terminator_func(_: str) -> str:
    global launched_instance_ids
    try:
        if not launched_instance_ids:
            return "⚠️ No previously launched EC2 instances to terminate."

        ec2 = boto3.resource("ec2")
        instances = ec2.instances.filter(InstanceIds=launched_instance_ids)
        for instance in instances:
            instance.terminate()

        terminated_ids = launched_instance_ids.copy()
        launched_instance_ids.clear()
        return f"🛑 Terminated EC2 Instances: {', '.join(terminated_ids)}"
    except Exception as e:
        return f"❌ Error terminating EC2 instances: {str(e)}"


# ✅ Define Tools
tools = [
    Tool(
        name="ec2_launcher",
        func=ec2_launcher_func,
        description=(
            "Launch EC2 instances based on user input. You can say things like:\n"
            "- 'Launch 2 t2.micro instances in ap-south-1'\n"
            "- 'Create 1 instance type t3.small in us-west-2'\n"
            "- 'Spin up EC2'\n"
        )
    ),
    Tool(
        name="ec2_terminator",
        func=ec2_terminator_func,
        description="Terminate all previously launched EC2 instances."
    )
]

# ✅ Load Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

# ✅ Initialize LangChain Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# ✅ Session State Setup
if "result" not in st.session_state:
    st.session_state.result = ""

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# ✅ Streamlit Input
user_prompt = st.text_area("💬 Enter your EC2 Command Prompt", height=150, placeholder="e.g. Launch 2 instances in ap-south-1 with t3.small")

# 🚀 Run Button
if st.button("🚀 Run Command"):
    if user_prompt.strip() == "":
        st.warning("Please enter a prompt.")
    else:
        st.session_state.last_prompt = user_prompt
        with st.spinner("🤖 Thinking..."):
            result = agent.invoke(user_prompt)
            st.session_state.result = result

# 🧹 Clear Button
if st.button("🧹 Clear"):
    st.session_state.result = ""
    st.session_state.last_prompt = ""
    user_prompt = ""

# 📤 Output Display
if st.session_state.result:
    st.code(st.session_state.result, language="text")
