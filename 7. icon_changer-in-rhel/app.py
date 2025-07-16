import streamlit as st
import os
import shutil

st.set_page_config(page_title="Linux App Icon Changer", layout="centered")
st.title("🖼️ Linux App Icon Changer (RHEL Friendly)")

# Step 1: List installed applications
system_app_dir = "/usr/share/applications/"
user_app_dir = os.path.expanduser("~/.local/share/applications/")
os.makedirs(user_app_dir, exist_ok=True)

desktop_files = [f for f in os.listdir(system_app_dir) if f.endswith(".desktop")]
app_choices = sorted([f.replace(".desktop", "") for f in desktop_files])

app_name = st.selectbox("🔍 Select the application", app_choices)

# Step 2: Upload new icon
uploaded_icon = st.file_uploader("📁 Upload a new icon (PNG, SVG, XPM)", type=["png", "svg", "xpm"])

# Step 3: Trigger change
if st.button("✅ Change Icon") and uploaded_icon:
    try:
        # Paths
        original_desktop = os.path.join(system_app_dir, f"{app_name}.desktop")
        target_desktop = os.path.join(user_app_dir, f"{app_name}.desktop")

        # Save uploaded icon
        icon_save_dir = os.path.expanduser("~/Pictures/icons/")
        os.makedirs(icon_save_dir, exist_ok=True)
        icon_path = os.path.join(icon_save_dir, uploaded_icon.name)
        with open(icon_path, "wb") as f:
            f.write(uploaded_icon.read())

        # Copy .desktop file to local user dir
        shutil.copyfile(original_desktop, target_desktop)

        # Modify Icon= line
        with open(target_desktop, "r") as f:
            lines = f.readlines()

        with open(target_desktop, "w") as f:
            for line in lines:
                if line.startswith("Icon="):
                    f.write(f"Icon={icon_path}\n")
                else:
                    f.write(line)

        st.success(f"Icon for '{app_name}' changed successfully! 🎉")
        st.info(f"If it doesn't update immediately, try logging out and back in.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
else:
    st.warning("Please select an app and upload an icon to proceed.")
