import streamlit as st
import subprocess
import shlex
import re

st.set_page_config(page_title="Remote SSH Interface", layout="wide")
st.title("🚀 Linux-Menu-Based-Project(GUI-CLI-Commands)")

COMMANDS = {
    "File Manager (Nautilus)": "/usr/bin/nautilus",
    "Text Editor (Gedit)": "/usr/bin/gedit",
    "System Monitor": "/usr/bin/gnome-system-monitor",
    "Terminal": "/usr/bin/gnome-terminal",
    "Software Updater": "/usr/bin/update-manager",
    "List directory contents": "/bin/ls",
    "Print working directory": "/bin/pwd",
    "Disk space usage": "/bin/df -h",
    "Memory usage": "/usr/bin/free -h",
    "Processes snapshot": "/usr/bin/top -n 1",
    "List all files": "/bin/ls -a",
    "System uptime": "/usr/bin/uptime",
    "Calendar": "/usr/bin/cal",
    "Date and time": "/bin/date",
    "USB devices": "/usr/bin/lsusb",
    "PCI devices": "/usr/bin/lspci",
    "Logged-in users": "/usr/bin/who",
    "Network interfaces": "/sbin/ifconfig",
    "Ping Google": "/bin/ping -c 4 google.com",
    "Environment variables": "/usr/bin/printenv",
    "Current user": "/usr/bin/whoami",
    "Kernel version": "/usr/bin/uname -r",
    "System info": "/usr/bin/uname -a",
    "Block devices": "/bin/lsblk"
}

output_data = {"stop": False, "output": ""}

# ---------- Helper Functions ----------
def is_valid_filename(filename):
    return bool(re.match(r'^[\w\-.]+$', filename))

def remote_file_exists(user, host, filename, password=None):
    cmd = f'ssh {user}@{host} "test -f {shlex.quote(filename)} && echo exists || echo notfound"'
    return run_ssh_command(cmd, password).strip() == "exists"

def run_ssh_command(cmd, password=None):
    try:
        if password:
            # Ensure sshpass is installed for password-based access
            full_cmd = f"sshpass -p {shlex.quote(password)} {cmd}"
        else:
            full_cmd = cmd
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout if result.returncode == 0 else result.stderr
    except subprocess.TimeoutExpired:
        return "⏱️ Command timed out."
    except Exception as e:
        return f"❌ Exception: {str(e)}"

def execute_ssh_command(user, host, command, save_output=False, remote_filename="", password=None):
    if output_data["stop"]:
        return "❌ Command stopped."

    if save_output:
        if not is_valid_filename(remote_filename):
            return "❗ Invalid filename."
        if remote_file_exists(user, host, remote_filename, password):
            return f"⚠ File '{remote_filename}' already exists."
        command = f"{command} > {remote_filename}"

    ssh_cmd = f'ssh {user}@{host} "bash -c {shlex.quote(command)}"'
    return run_ssh_command(ssh_cmd, password).strip()

# ---------- UI Section ----------
st.markdown("### 🔐 SSH Connection Details")

col1, col2, col3 = st.columns(3)
with col1:
    user = st.text_input("👤 SSH Username", value="root")
with col2:
    host = st.text_input("🌐 Remote IP", placeholder="e.g. 192.168.1.100")
with col3:
    auth_method = st.selectbox("🔐 Authentication Method", ["SSH Key (default)", "Password"])

password = None
if auth_method == "Password":
    password = st.text_input("🔑 Password", type="password")

# ---------- Command Options ----------
st.markdown("### ⚙️ Command Options")

use_custom = st.toggle("Use Custom Command", value=False)

if use_custom:
    command_input = st.text_input("💡 Enter Custom Command", placeholder="e.g., ls -la /etc")
else:
    selected_command = st.selectbox("📜 Predefined Commands", list(COMMANDS.keys()))
    command_input = COMMANDS[selected_command]

# ---------- Output Saving ----------
save_output = st.checkbox("💾 Save output to a remote file?")
remote_filename = ""
if save_output:
    remote_filename = st.text_input("📝 Remote Filename")

# ---------- Command Buttons ----------
if "stop_flag" not in st.session_state:
    st.session_state.stop_flag = False

run = st.button("▶ Run Command")
stop = st.button("🛑 Stop Command")

if stop:
    output_data["stop"] = True
    st.warning("🛑 Stop signal sent. The next execution will be halted.")

# ---------- Output Display ----------
if run:
    output = execute_ssh_command(
        user=user,
        host=host,
        command=command_input,
        save_output=save_output,
        remote_filename=remote_filename,
        password=password
    )
    st.text_area("📤 Command Output", value=output, height=300)
